/**
 * Renders the human-study forms from form_spec.json (fixture build).
 * Apps Script is a thin renderer: all content and checks live in build_spec.py
 * and test_spec.py. Untested against live Google until the first run.
 *
 * Before running:
 *  1. Upload form_spec.json and assignment_fixture.csv to the team's restricted Drive folder.
 *  2. Fill CONFIG with their file IDs and a TEST response sheet ID.
 *  3. Run renderAll() once and approve the permissions.
 * Output: four forms (Form 1 to Form 4, one per variant in the spec) and a sheet "Assignment links (fixture)".
 * Keep ACCEPTING_RESPONSES false except during a test.
 */
const CONFIG = {
  SPEC_FILE_ID: 'PASTE_FILE_ID',
  ASSIGNMENT_FILE_ID: 'PASTE_FILE_ID',
  RESPONSE_SHEET_ID: 'PASTE_TEST_SHEET_ID',
  ACCEPTING_RESPONSES: false,
};

function renderAll() {
  const spec = JSON.parse(readDriveText_(CONFIG.SPEC_FILE_ID));
  const forms = {};
  spec.variants.forEach(function (v) {
    forms[v.variant_id] = buildForm_(spec, v);
  });
  writeLinks_(forms);
}

function readDriveText_(fileId) {
  return DriveApp.getFileById(fileId).getBlob().getDataAsString('UTF-8');
}

function buildForm_(spec, v) {
  const form = FormApp.create(spec.form_title + ' - ' + v.form_label);
  form.setCollectEmail(false)
    .setAllowResponseEdits(false)
    .setLimitOneResponsePerUser(false)
    .setPublishingSummary(false)
    .setShowLinkToRespondAgain(false)
    .setAcceptingResponses(CONFIG.ACCEPTING_RESPONSES)
    .setConfirmationMessage(spec.confirmation || spec.debrief);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, CONFIG.RESPONSE_SHEET_ID);

  const pages = {};
  const pending = [];
  v.sections.forEach(function (sec, i) {
    if (i === 0) {
      form.setTitle(spec.form_title);
      form.setDescription(sec.title + '\n\n' + sec.description);
    } else {
      pages[sec.id] = form.addPageBreakItem().setTitle(sec.title).setHelpText(sec.description || '');
    }
    sec.items.forEach(function (it) {
      addItem_(form, it, pending);
    });
  });

  // Navigation needs every page to exist, so choices are set last.
  pending.forEach(function (p) {
    // Google rejects a mix of routed and unrouted answers, so unrouted ones get CONTINUE.
    const hasRoutes = Object.keys(p.goto).length > 0;
    const choices = p.labels.map(function (label) {
      const target = p.goto[label];
      if (!target) return hasRoutes ? p.item.createChoice(label, FormApp.PageNavigationType.CONTINUE) : p.item.createChoice(label);
      if (target === 'SUBMIT') return p.item.createChoice(label, FormApp.PageNavigationType.SUBMIT);
      return p.item.createChoice(label, pages[target]);
    });
    try {
      p.item.setChoices(choices);
    } catch (e) {
      Logger.log('ROUTE BY HAND: "' + p.item.getTitle() + '" ' + JSON.stringify(p.goto));
      p.item.setChoices(p.labels.map(function (label) { return p.item.createChoice(label); }));
    }
  });

  // A section marked after = SUBMIT ends the form there, so completers never reach the decline page.
  v.sections.forEach(function (sec, i) {
    const next = v.sections[i + 1];
    if (sec.after !== 'SUBMIT' || !next) return;
    try {
      pages[next.id].setGoToPage(FormApp.PageNavigationType.SUBMIT);
    } catch (e) {
      Logger.log('ROUTE BY HAND: after section "' + sec.title + '" choose Submit form');
    }
  });
  return form;
}

function addItem_(form, it, pending) {
  const required = it.required !== false;
  switch (it.type) {
    case 'multiple_choice': {
      const item = form.addMultipleChoiceItem().setTitle(it.title).setRequired(required);
      pending.push({ item: item, labels: it.choices, goto: it.goto_map || {} });
      break;
    }
    case 'scale':
      form.addScaleItem().setTitle(it.title).setBounds(it.low, it.high)
        .setLabels(it.low_label, it.high_label).setRequired(required);
      break;
    case 'paragraph':
      form.addParagraphTextItem().setTitle(it.title).setHelpText(it.help || '').setRequired(required);
      break;
    case 'short_text':
      form.addTextItem().setTitle(it.title).setHelpText(it.help || '').setRequired(required);
      break;
    case 'text_block':
      form.addSectionHeaderItem().setTitle(it.title).setHelpText(it.text || '');
      break;
    default:
      throw new Error('Unknown item type: ' + it.type);
  }
}

/** Writes each slot's pre-filled link (code and variant) to a new sheet. */
function writeLinks_(forms) {
  const rows = Utilities.parseCsv(readDriveText_(CONFIG.ASSIGNMENT_FILE_ID));
  const head = rows[0];
  const iCode = head.indexOf('participant_code');
  const iVariant = head.indexOf('variant_id');
  const out = [head.concat(['prefilled_link'])];
  for (let r = 1; r < rows.length; r++) {
    const form = forms[rows[r][iVariant]];
    const codeItem = form.getItems(FormApp.ItemType.TEXT).filter(function (i) {
      return i.getTitle() === 'Your participant code';
    })[0];
    const response = form.createResponse()
      .withItemResponse(codeItem.asTextItem().createResponse(rows[r][iCode]));
    out.push(rows[r].concat([response.toPrefilledUrl()]));
  }
  const ss = SpreadsheetApp.create('Assignment links (fixture)');
  const sheet = ss.getSheets()[0];
  sheet.getRange(1, 1, out.length, out[0].length).setValues(out);
  Logger.log('Links sheet: ' + ss.getUrl());
}
