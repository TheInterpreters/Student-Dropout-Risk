param(
    [string]$OutputPath = (Join-Path (Resolve-Path '.').Path 'Final_Report\Student_Dropout_Risk_Presentation.pptx')
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path '.').Path
$outDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

# Palette: light academic canvas with navy emphasis slides.
$NAVY = 0x4F3216       # #16324F in Office BGR integer order
$TEAL = 0x8C8C16       # #168C8C
$GOLD = 0x3CA2E6       # #E6A23C
$SOFTBLUE = 0xF3EADC   # #DCEAF3
$OFFWHITE = 0xFBF9F7   # #F7F9FB
$CHARCOAL = 0x383226   # #263238
$MUTEDRED = 0x5555C9   # #C95555
$WHITE = 0xFFFFFF
$MIDGREY = 0x786E68
$LIGHTGREY = 0xE8E5E2

$ppLayoutBlank = 12
$ppSaveAsOpenXMLPresentation = 24
$ppSaveAsPDF = 32
$msoFalse = 0
$msoTrue = -1
$msoTextOrientationHorizontal = 1
$msoShapeRectangle = 1
$msoShapeRoundedRectangle = 5
$msoShapeOval = 9
$msoShapeChevron = 52
$msoShapeRightArrow = 33

function Add-Text {
    param($Slide, [string]$Text, [double]$X, [double]$Y, [double]$W, [double]$H,
          [double]$Size = 20, [int]$Color = $CHARCOAL, [bool]$Bold = $false,
          [int]$Align = 1, [string]$Font = 'Aptos', [double]$Margin = 4)
    $s = $Slide.Shapes.AddTextbox($msoTextOrientationHorizontal, $X, $Y, $W, $H)
    $s.TextFrame.MarginLeft = $Margin
    $s.TextFrame.MarginRight = $Margin
    $s.TextFrame.MarginTop = 2
    $s.TextFrame.MarginBottom = 2
    $s.TextFrame.WordWrap = $msoTrue
    $s.TextFrame.AutoSize = 0
    $r = $s.TextFrame.TextRange
    $r.Text = $Text
    $r.Font.Name = $Font
    $r.Font.Size = $Size
    $r.Font.Bold = $(if ($Bold) { $msoTrue } else { $msoFalse })
    $r.Font.Color.RGB = $Color
    $r.ParagraphFormat.Alignment = $Align
    return $s
}

function Add-Box {
    param($Slide, [double]$X, [double]$Y, [double]$W, [double]$H,
          [int]$Fill = $WHITE, [int]$Line = $LIGHTGREY, [double]$Radius = 0,
          [double]$LineWeight = 1)
    $kind = $(if ($Radius -gt 0) { $msoShapeRoundedRectangle } else { $msoShapeRectangle })
    $s = $Slide.Shapes.AddShape($kind, $X, $Y, $W, $H)
    $s.Fill.ForeColor.RGB = $Fill
    $s.Line.ForeColor.RGB = $Line
    $s.Line.Weight = $LineWeight
    return $s
}

function Add-Line {
    param($Slide, [double]$X1, [double]$Y1, [double]$X2, [double]$Y2,
          [int]$Color = $TEAL, [double]$Weight = 2, [bool]$Arrow = $false)
    $s = $Slide.Shapes.AddLine($X1, $Y1, $X2, $Y2)
    $s.Line.ForeColor.RGB = $Color
    $s.Line.Weight = $Weight
    if ($Arrow) { $s.Line.EndArrowheadStyle = 3 }
    return $s
}

function Add-PictureFit {
    param($Slide, [string]$Path, [double]$X, [double]$Y, [double]$W, [double]$H,
          [bool]$Border = $false)
    $full = (Resolve-Path $Path).Path
    $pic = $Slide.Shapes.AddPicture($full, $msoFalse, $msoTrue, $X, $Y, -1, -1)
    $scale = [Math]::Min($W / $pic.Width, $H / $pic.Height)
    $pic.Width = $pic.Width * $scale
    $pic.Height = $pic.Height * $scale
    $pic.Left = $X + ($W - $pic.Width) / 2
    $pic.Top = $Y + ($H - $pic.Height) / 2
    if ($Border) {
        $pic.Line.Visible = $msoTrue
        $pic.Line.ForeColor.RGB = $LIGHTGREY
        $pic.Line.Weight = 1
    }
    return $pic
}

function Add-Title {
    param($Slide, [string]$Title, [bool]$Dark = $false, [string]$Kicker = '')
    $tc = $(if ($Dark) { $WHITE } else { $NAVY })
    if ($Kicker) { Add-Text $Slide $Kicker 42 20 870 20 10 $(if ($Dark) {$GOLD} else {$TEAL}) $true | Out-Null }
    Add-Text $Slide $Title 42 40 870 42 27 $tc $true | Out-Null
    Add-Line $Slide 42 88 918 88 $(if ($Dark) {$TEAL} else {$SOFTBLUE}) 2 | Out-Null
}

function Add-Footer {
    param($Slide, [int]$Number, [bool]$Dark = $false, [string]$Label = 'AIT XDS | The Interpreters')
    $c = $(if ($Dark) { 0xD8D2CC } else { $MIDGREY })
    Add-Text $Slide $Label 42 520 760 16 9 $c $false | Out-Null
    Add-Text $Slide ([string]$Number) 870 520 45 16 9 $c $false 3 | Out-Null
}

function New-Slide {
    param($Presentation, [bool]$Dark = $false)
    $sl = $Presentation.Slides.Add($Presentation.Slides.Count + 1, $ppLayoutBlank)
    $sl.FollowMasterBackground = $msoFalse
    $bg = $sl.Background.Fill
    $bg.Solid()
    $bg.ForeColor.RGB = $(if ($Dark) { $NAVY } else { $OFFWHITE })
    return $sl
}

function Add-Pill {
    param($Slide, [string]$Text, [double]$X, [double]$Y, [double]$W,
          [int]$Fill = $SOFTBLUE, [int]$TextColor = $NAVY)
    Add-Box $Slide $X $Y $W 28 $Fill $Fill 8 | Out-Null
    Add-Text $Slide $Text $X ($Y + 4) $W 18 11 $TextColor $true 2 | Out-Null
}

function Add-KPI {
    param($Slide, [string]$Value, [string]$Label, [double]$X, [double]$Y, [double]$W,
          [int]$Accent = $TEAL, [bool]$Dark = $false)
    $fill = $(if ($Dark) { 0x684526 } else { $WHITE })
    $line = $(if ($Dark) { $TEAL } else { $SOFTBLUE })
    $text = $(if ($Dark) { $WHITE } else { $CHARCOAL })
    Add-Box $Slide $X $Y $W 112 $fill $line 8 1.5 | Out-Null
    Add-Text $Slide $Value ($X + 12) ($Y + 15) ($W - 24) 40 29 $Accent $true 2 | Out-Null
    Add-Text $Slide $Label ($X + 12) ($Y + 63) ($W - 24) 36 12 $text $false 2 | Out-Null
}

function Add-Bullets {
    param($Slide, [string[]]$Items, [double]$X, [double]$Y, [double]$W, [double]$H,
          [double]$Size = 17, [int]$Color = $CHARCOAL, [int]$Accent = $TEAL)
    $n = $Items.Count
    $row = $H / [Math]::Max($n, 1)
    for ($i=0; $i -lt $n; $i++) {
        $cy = $Y + $i * $row + 7
        $dot = $Slide.Shapes.AddShape($msoShapeOval, $X, $cy + 5, 9, 9)
        $dot.Fill.ForeColor.RGB = $Accent
        $dot.Line.Visible = $msoFalse
        Add-Text $Slide $Items[$i] ($X + 20) $cy ($W - 20) ($row - 2) $Size $Color $false | Out-Null
    }
}

function Add-Table {
    param($Slide, [object[][]]$Rows, [double]$X, [double]$Y, [double]$W, [double]$H,
          [double]$FontSize = 12, [int]$HeaderFill = $NAVY, [int]$HeaderText = $WHITE,
          [int[]]$Widths = @())
    $rCount = $Rows.Count
    $cCount = $Rows[0].Count
    $shape = $Slide.Shapes.AddTable($rCount, $cCount, $X, $Y, $W, $H)
    $tbl = $shape.Table
    if ($Widths.Count -eq $cCount) {
        $sum = ($Widths | Measure-Object -Sum).Sum
        for ($c=1; $c -le $cCount; $c++) { $tbl.Columns.Item($c).Width = $W * $Widths[$c-1] / $sum }
    }
    for ($r=1; $r -le $rCount; $r++) {
        for ($c=1; $c -le $cCount; $c++) {
            $cell = $tbl.Cell($r,$c).Shape
            $cell.TextFrame.TextRange.Text = [string]$Rows[$r-1][$c-1]
            $cell.TextFrame.TextRange.Font.Name = 'Aptos'
            $cell.TextFrame.TextRange.Font.Size = $FontSize
            $cell.TextFrame.TextRange.Font.Color.RGB = $(if ($r -eq 1) { $HeaderText } else { $CHARCOAL })
            $cell.TextFrame.TextRange.Font.Bold = $(if ($r -eq 1) { $msoTrue } else { $msoFalse })
            $cell.TextFrame.TextRange.ParagraphFormat.Alignment = $(if ($c -eq 1) { 1 } else { 2 })
            $cell.TextFrame.VerticalAnchor = 3
            $cell.Fill.ForeColor.RGB = $(if ($r -eq 1) { $HeaderFill } elseif ($r % 2 -eq 0) { $WHITE } else { $OFFWHITE })
            $cell.TextFrame.MarginLeft = 5
            $cell.TextFrame.MarginRight = 5
        }
    }
    return $shape
}

function Add-Notes {
    param($Slide, [string]$Text)
    try {
        foreach ($sh in $Slide.NotesPage.Shapes) {
            if ($sh.PlaceholderFormat.Type -eq 2) {
                $sh.TextFrame.TextRange.Text = $Text
                break
            }
        }
    } catch { }
}

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = $msoTrue
$pres = $ppt.Presentations.Add()
$pres.PageSetup.SlideWidth = 960
$pres.PageSetup.SlideHeight = 540

try {
    # 1 - title (light)
    $s = New-Slide $pres $false
    Add-Pill $s 'AIT | EXPLAINABLE DATA SCIENCE' 54 38 250 $SOFTBLUE $NAVY
    Add-Text $s 'Evaluating the Trustworthiness of Explanations for Student Dropout Risk' 54 103 850 104 30 $NAVY $true | Out-Null
    Add-Text $s 'Comparing Black-Box and Interpretable Models' 58 216 780 36 20 $TEAL $false | Out-Null
    Add-Line $s 58 273 902 273 $GOLD 4 | Out-Null
    Add-Text $s 'Aye Khin Khin Hpone (Yolanda Lim) | Nguyen Liem Son (Lucas) | Witchayda Theppithuk (Noey)' 58 315 835 24 13 $CHARCOAL $false | Out-Null
    Add-Text $s 'Han Htoo Zaw (Han) | Pyae Sone Han (Harry)' 58 345 835 24 13 $CHARCOAL $false | Out-Null
    Add-Text $s 'Locked model comparison | explanation audit | 50-person human study' 58 424 835 30 15 $MIDGREY $false | Out-Null
    Add-Footer $s 1 $false
    Add-Notes $s 'Timing: 0:40. Open with the decision problem, not the algorithm. State that the study asks whether a complex model and its explanations are justified.'

    # 2 - decision setting (light)
    $s = New-Slide $pres $false; Add-Title $s 'The real decision is a capacity-limited contact list' $false 'MOTIVATION'
    Add-KPI $s '20%' 'Assumed share of a cohort that the support office can contact' 52 120 250 $TEAL
    Add-KPI $s 'After S1' 'Prediction point: after first-semester results are available' 355 120 250 $GOLD
    Add-KPI $s 'Support' 'A flag offers a conversation; it never denies assistance' 658 120 250 $TEAL
    Add-Box $s 52 275 856 158 $WHITE $SOFTBLUE 8 1.5 | Out-Null
    Add-Text $s 'Score -> rank -> contact the top one in five' 76 296 805 36 22 $NAVY $true 2 | Out-Null
    Add-Line $s 165 355 795 355 $TEAL 4 $true | Out-Null
    foreach ($p in @(@(150,'Student records'),@(390,'Risk ranking'),@(660,'Adviser review'))) {
        $o=$s.Shapes.AddShape($msoShapeOval,$p[0],335,48,48); $o.Fill.ForeColor.RGB=$SOFTBLUE; $o.Line.ForeColor.RGB=$TEAL
        Add-Text $s $p[1] ($p[0]-48) 392 145 28 12 $CHARCOAL $true 2 | Out-Null
    }
    Add-Footer $s 2 $false
    Add-Notes $s 'Timing: 1:20. Explain asymmetric errors: a missed student may receive no offer; an unnecessary flag uses a scarce meeting. Stress human review.'

    # 3 - questions (dark)
    $s = New-Slide $pres $true; Add-Title $s 'Three questions organise the study' $true 'RESEARCH QUESTIONS'
    $rq = @(
        @('RQ1','Predictive value','Does TabICL add value over conventional and interpretable baselines at the same 20% capacity?'),
        @('RQ2','Explanation trustworthiness','Are the local explanations faithful, stable and appropriately constrained?'),
        @('RQ3','Human usefulness','Do explanation charts help people anticipate the model''s outreach flag?')
    )
    for($i=0;$i -lt 3;$i++) {
        $y=122+$i*118
        Add-Box $s 64 $y 832 92 0x684526 $TEAL 8 1.3 | Out-Null
        Add-Text $s $rq[$i][0] 82 ($y+18) 70 42 22 $GOLD $true 2 | Out-Null
        Add-Text $s $rq[$i][1] 168 ($y+12) 250 28 17 $WHITE $true | Out-Null
        Add-Text $s $rq[$i][2] 168 ($y+41) 690 36 13 0xE8E5E2 $false | Out-Null
    }
    Add-Footer $s 3 $true
    Add-Notes $s 'Timing: 1:00. State the three questions exactly and use them as signposts throughout the talk.'

    # 4 - data
    $s = New-Slide $pres $false; Add-Title $s 'One public cohort, one frozen split, one locked test' $false 'DATA DESIGN'
    Add-KPI $s '4,424' 'Original UCI records: Dropout, Enrolled and Graduate' 52 112 260 $TEAL
    Add-KPI $s '3,630' 'Binary cohort after excluding 794 still-enrolled outcomes' 350 112 260 $GOLD
    Add-KPI $s '33' 'Inputs after first semester; all second-semester fields removed' 648 112 260 $TEAL
    $parts=@(@('TRAIN','2,541','70%'),@('VALIDATION','544','15%'),@('LOCKED TEST','545','15%'))
    for($i=0;$i -lt 3;$i++) {
        $x=68+$i*292
        Add-Box $s $x 292 238 110 $(if($i -eq 2){0xEEF5FF}else{$WHITE}) $(if($i -eq 2){$GOLD}else{$SOFTBLUE}) 8 1.5 | Out-Null
        Add-Text $s $parts[$i][0] ($x+12) 308 214 20 11 $(if($i -eq 2){$GOLD}else{$TEAL}) $true 2 | Out-Null
        Add-Text $s $parts[$i][1] ($x+12) 336 214 35 27 $NAVY $true 2 | Out-Null
        Add-Text $s $parts[$i][2] ($x+12) 375 214 18 11 $MIDGREY $false 2 | Out-Null
    }
    Add-Text $s 'Stratified once | seed 42 | every modelling choice fixed on validation' 82 438 790 25 14 $CHARCOAL $true 2 | Out-Null
    Add-Footer $s 4 $false
    Add-Notes $s 'Timing: 1:25. Explain why Enrolled was excluded and why that remains a deployment limitation. Mention the prediction window and frozen IDs.'

    # 5 - workflow native diagram
    $s = New-Slide $pres $false; Add-Title $s 'The test was protected from iterative model selection' $false 'FROZEN WORKFLOW'
    $steps=@('Decision frame','Data design','Model development','Validation freeze','One-time final test','Local explanations','Post-hoc audit','Human study','Deliverables')
    for($i=0;$i -lt 9;$i++) {
        $row=[Math]::Floor($i/3); $col=$i%3
        if($row -eq 1){$col=2-$col}
        $x=58+$col*292; $y=112+$row*118
        $fill=$(if($i -eq 6 -or $i -eq 8){0xEAF4FC}else{$WHITE})
        $line=$(if($i -eq 6 -or $i -eq 8){$GOLD}else{$TEAL})
        Add-Box $s $x $y 240 70 $fill $line 8 1.3 | Out-Null
        Add-Text $s ([string]($i+1)) ($x+10) ($y+19) 30 26 16 $line $true 2 | Out-Null
        Add-Text $s $steps[$i] ($x+45) ($y+17) 180 32 14 $NAVY $true | Out-Null
        if($i -lt 8) {
            if($i -eq 2 -or $i -eq 5){ Add-Line $s ($x+120) ($y+70) ($x+120) ($y+110) $MIDGREY 1.5 $true | Out-Null }
            else {
                $dir=$(if($row -eq 1){-1}else{1}); Add-Line $s ($x+120+$dir*120) ($y+35) ($x+120+$dir*166) ($y+35) $MIDGREY 1.5 $true | Out-Null
            }
        }
    }
    Add-Pill $s 'Orange = added after the locked test without changing the model' 250 473 460 0xEEF5FF $CHARCOAL
    Add-Footer $s 5 $false
    Add-Notes $s 'Timing: 1:20. Highlight the hash and lock file. The full explanation audit was post-hoc but used validation only and did not alter the model.'

    # 6 - methods (dark)
    $s = New-Slide $pres $true; Add-Title $s 'Complexity was tested against strong, simpler baselines' $true 'MODELS AND EVALUATION'
    $models=@(
        @('Logistic regression','Interpretable','Linear baseline'),
        @('Depth-3 tree','Interpretable','Small rule set'),
        @('XGBoost','Black box','Tuned boosting'),
        @('Main-effects EBM','Interpretable','Shape functions, no interactions'),
        @('TabICL','Black box','Tabular foundation model')
    )
    for($i=0;$i -lt 5;$i++) {
        $x=52+$i*176
        Add-Box $s $x 124 156 160 0x684526 $(if($i -eq 4){$GOLD}else{$TEAL}) 8 1.3 | Out-Null
        Add-Text $s $models[$i][0] ($x+10) 145 136 46 16 $WHITE $true 2 | Out-Null
        Add-Pill $s $models[$i][1] ($x+18) 202 120 $(if($models[$i][1] -eq 'Interpretable'){$TEAL}else{$GOLD}) $NAVY
        Add-Text $s $models[$i][2] ($x+10) 244 136 24 11 0xE8E5E2 $false 2 | Out-Null
    }
    Add-Text $s 'Same operating point for every model' 60 330 840 25 18 $GOLD $true 2 | Out-Null
    Add-Bullets $s @('Top 20% flagged by cohort rank','ROC-AUC and Brier score','Recall and precision at capacity','Paired bootstrap intervals: 2,000 resamples') 72 370 820 110 14 $WHITE $TEAL
    Add-Footer $s 6 $true
    Add-Notes $s 'Timing: 1:15. Describe TabICL as the candidate, EBM as the key transparent comparator, and capacity metrics as the decision-relevant measures.'

    # 7 - predictive figure
    $s = New-Slide $pres $false; Add-Title $s 'TabICL ranked well, but did not separate from EBM or XGBoost' $false 'LOCKED FINAL TEST | n = 545'
    Add-PictureFit $s 'figures\report_ready\final_test_model_performance.png' 55 108 570 350 $true | Out-Null
    Add-KPI $s '0.957' 'TabICL ROC-AUC' 660 120 235 $TEAL
    Add-KPI $s '0.954' 'EBM ROC-AUC' 660 252 235 $GOLD
    Add-Box $s 660 384 235 70 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s 'Delta = 0.003' 675 397 205 25 18 $NAVY $true 2 | Out-Null
    Add-Text $s '95% CI -0.007 to 0.014' 675 425 205 18 11 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 7 $false
    Add-Notes $s 'Timing: 1:30. Avoid saying models are equal. Say the observed differences were small and the paired intervals included zero for TabICL versus EBM, XGBoost and logistic regression.'

    # 8 - capacity result
    $s = New-Slide $pres $false; Add-Title $s 'Near-perfect precision coexists with missed dropouts' $false 'DECISION PERFORMANCE'
    Add-KPI $s '109' 'Students flagged in the locked test' 52 116 250 $TEAL
    Add-KPI $s '108' 'Flagged students who later dropped out' 355 116 250 $GOLD
    Add-KPI $s '105' 'Dropouts not flagged at 20% capacity' 658 116 250 $MUTEDRED
    Add-PictureFit $s 'figures\report_ready\final_test_outreach_metrics.png' 85 272 430 202 $false | Out-Null
    Add-Box $s 548 284 338 168 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s 'Precision  0.991' 575 305 285 28 19 $NAVY $true | Out-Null
    Add-Text $s 'Recall      0.507' 575 345 285 28 19 $NAVY $true | Out-Null
    Add-Line $s 574 384 854 384 $LIGHTGREY 1 | Out-Null
    Add-Text $s 'With 109 slots and 213 dropouts, recall cannot exceed about 0.51.' 575 399 285 40 12 $MIDGREY $false | Out-Null
    Add-Footer $s 8 $false
    Add-Notes $s 'Timing: 1:30. The high precision is real but does not imply comprehensive screening. Capacity mathematically limits recall.'

    # 9 - uncertainty (dark)
    $s = New-Slide $pres $true; Add-Title $s 'The added complexity is not supported by the uncertainty' $true 'PAIRED BOOTSTRAP: TabICL - BASELINE ROC-AUC'
    $comparisons=@(
        @('Logistic regression','+0.004','-0.005 to +0.014'),
        @('Decision tree','+0.047','+0.029 to +0.067'),
        @('XGBoost','+0.001','-0.006 to +0.009'),
        @('EBM','+0.003','-0.007 to +0.014')
    )
    for($i=0;$i -lt 4;$i++) {
        $y=118+$i*82
        Add-Text $s $comparisons[$i][0] 70 ($y+10) 210 24 15 $WHITE $true | Out-Null
        Add-Text $s $comparisons[$i][1] 295 ($y+8) 110 28 20 $(if($i -eq 1){$GOLD}else{$TEAL}) $true 2 | Out-Null
        Add-Text $s $comparisons[$i][2] 425 ($y+10) 260 24 14 0xE8E5E2 $false | Out-Null
        Add-Line $s 700 ($y+21) 865 ($y+21) 0xA6A19C 3 | Out-Null
        Add-Line $s 782 ($y+2) 782 ($y+40) $WHITE 1 | Out-Null
        $dot=$s.Shapes.AddShape($msoShapeOval, $(if($i -eq 1){824}else{780}), ($y+15), 12, 12); $dot.Fill.ForeColor.RGB=$(if($i -eq 1){$GOLD}else{$TEAL}); $dot.Line.Visible=$msoFalse
    }
    Add-Text $s 'Only the small tree was clearly worse.' 70 464 820 28 19 $GOLD $true 2 | Out-Null
    Add-Footer $s 9 $true
    Add-Notes $s 'Timing: 1:10. Explain the zero line. The decision-tree interval excludes zero; the other three do not.'

    # 10 - who is flagged
    $s = New-Slide $pres $false; Add-Title $s 'Most flags restate visible first-semester disengagement' $false 'WHO GETS FLAGGED? | VALIDATION'
    Add-KPI $s '108' 'Flagged validation students' 52 112 250 $TEAL
    Add-KPI $s '78' 'Had passed no first-semester units' 355 112 250 $GOLD
    Add-KPI $s '93' 'Unflagged dropouts had passed at least 1 unit' 658 112 250 $MUTEDRED
    Add-Box $s 62 274 836 164 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s 'What the list adds' 92 296 220 25 16 $TEAL $true | Out-Null
    Add-Text $s 'Ordering of obvious high-risk records' 92 330 320 30 20 $NAVY $true | Out-Null
    Add-Text $s 'What remains difficult' 520 296 250 25 16 $GOLD $true | Out-Null
    Add-Text $s 'Finding less-visible students who later leave' 520 330 320 48 20 $NAVY $true | Out-Null
    Add-Line $s 464 294 464 413 $LIGHTGREY 2 | Out-Null
    Add-Text $s 'A simple transcript query could identify many of the clearest cases.' 95 393 740 24 13 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 10 $false
    Add-Notes $s 'Timing: 1:25. High precision partly comes from students who are already visibly disengaged; the important operational question is incremental benefit.'

    # 11 - explanation content
    $s = New-Slide $pres $false; Add-Title $s 'Explanations are faithful - but dominated by one visible signal' $false 'EXPLANATION AUDIT | 544 VALIDATION STUDENTS'
    Add-PictureFit $s 'figures\report_ready\top_explanation_groups.png' 52 112 555 350 $true | Out-Null
    Add-KPI $s '536/544' 'Positive deletion-faithfulness cases' 640 122 260 $TEAL
    Add-KPI $s '17/108' 'Flags with a fee/debt recourse candidate' 640 258 260 $GOLD
    Add-Box $s 640 394 260 62 $WHITE $SOFTBLUE 8 1.2 | Out-Null
    Add-Text $s 'Association is not cause' 653 408 234 22 17 $MUTEDRED $true 2 | Out-Null
    Add-Text $s 'A score change is not an intervention effect.' 653 432 234 16 10 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 11 $false
    Add-Notes $s 'Timing: 1:30. Define deletion faithfulness. First-semester progress was the leading reason for every flagged student. Explain why fee recourse is model behaviour, not advice.'

    # 12 - stability (dark)
    $s = New-Slide $pres $true; Add-Title $s 'Top reasons depend on how the explanation is recomputed' $true 'STABILITY'
    Add-PictureFit $s 'figures\report_ready\explanation_stability.png' 62 112 520 340 $true | Out-Null
    Add-KPI $s '411' 'Below 0.80 overlap when the comparison group changed' 620 126 276 $GOLD $true
    Add-KPI $s '213' 'Below 0.80 overlap across random seeds' 620 268 276 $TEAL $true
    Add-Text $s 'Minimal grade perturbations were stable in the tested setting.' 623 417 270 38 12 $WHITE $false 2 | Out-Null
    Add-Footer $s 12 $true
    Add-Notes $s 'Timing: 1:25. Distinguish background and seed instability from the tested minimal-grade perturbation stability. Recommend showing uncertainty rather than a precise ranking.'

    # 13 - human study design
    $s = New-Slide $pres $false; Add-Title $s 'A two-group study tested whether charts help people predict the flag' $false 'HUMAN STUDY | n = 50'
    Add-Box $s 55 125 245 245 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s '25 participants' 72 146 210 27 20 $NAVY $true 2 | Out-Null
    Add-Pill $s 'Profiles only' 92 190 170 $TEAL $WHITE
    Add-Text $s 'Student profile' 80 246 195 24 14 $CHARCOAL $true 2 | Out-Null
    Add-Text $s 'Predict the hidden flag' 80 282 195 24 14 $CHARCOAL $true 2 | Out-Null
    Add-Text $s 'Confidence + 3 written answers' 80 318 195 32 12 $MIDGREY $false 2 | Out-Null
    Add-Box $s 660 125 245 245 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s '25 participants' 677 146 210 27 20 $NAVY $true 2 | Out-Null
    Add-Pill $s 'Profile + chart' 697 190 170 $GOLD $NAVY
    Add-Text $s 'Same student profile' 685 246 195 24 14 $CHARCOAL $true 2 | Out-Null
    Add-Text $s '+ five SHAP bars' 685 282 195 24 14 $CHARCOAL $true 2 | Out-Null
    Add-Text $s 'Confidence + 3 written answers' 685 318 195 32 12 $MIDGREY $false 2 | Out-Null
    $arrow=$s.Shapes.AddShape($msoShapeRightArrow,365,195,230,90); $arrow.Fill.ForeColor.RGB=$SOFTBLUE; $arrow.Line.ForeColor.RGB=$TEAL
    Add-Text $s '10 scored cases\n5 flagged | 5 unflagged' 390 214 180 52 16 $NAVY $true 2 | Out-Null
    Add-Text $s 'Seeded assignment | two case orders | 500 scored responses | all participants retained' 85 408 790 38 14 $CHARCOAL $true 2 | Out-Null
    Add-Footer $s 13 $false
    Add-Notes $s 'Timing: 1:25. Clarify that this is forward simulation, not an intervention study and not a study with practising support officers.'

    # 14 - human quantitative
    $s = New-Slide $pres $false; Add-Title $s 'Charts increased confidence, not predictive accuracy' $false 'PARTICIPANT-LEVEL RESULTS'
    Add-PictureFit $s 'figures\human_study\human_accuracy_by_group.png' 45 118 380 305 $true | Out-Null
    $rows=[object[][]]@(
        @('Metric','Profiles','+ Charts','Difference [95% CI]'),
        @('Accuracy','0.916','0.900','-0.016 [-0.060, 0.032]'),
        @('Confidence','4.14','4.35','+0.21 [0.02, 0.42]'),
        @('Minutes','33.4','30.2','-3.2 [-8.7, 2.0]')
    )
    Add-Table $s $rows 455 139 455 205 13 $NAVY $WHITE @(25,18,18,39) | Out-Null
    Add-Box $s 468 374 430 74 $WHITE $SOFTBLUE 8 1.2 | Out-Null
    Add-Text $s 'No evidence that the charts improved flag prediction.' 485 390 395 26 17 $NAVY $true 2 | Out-Null
    Add-Text $s 'Exploratory accuracy p = 0.61; Hedges'' g = -0.19.' 485 421 395 18 11 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 14 $false
    Add-Notes $s 'Timing: 1:30. Lead with the confidence interval, not the p-value. Do not claim charts reduced accuracy generally; say the study found no evidence of an improvement.'

    # 15 - C01 (dark)
    $s = New-Slide $pres $true; Add-Title $s 'One unflagged case exposes a communication hazard' $true 'CASE C01'
    Add-PictureFit $s 'figures\human_study\human_accuracy_by_case.png' 50 112 555 348 $true | Out-Null
    Add-KPI $s '0.60 -> 0.20' 'Accuracy without versus with the chart on C01' 638 130 265 $GOLD $true
    Add-Box $s 638 276 265 168 0x684526 $TEAL 8 1.3 | Out-Null
    Add-Text $s 'Why?' 658 295 225 25 17 $GOLD $true | Out-Null
    Add-Text $s 'Several bars pushed risk upward, but the chart did not show the cohort cut-off. More concern was easily read as flagged.' 658 329 225 90 13 $WHITE $false | Out-Null
    Add-Footer $s 15 $true
    Add-Notes $s 'Timing: 1:20. C01 drives the overall difference, but leave-one-case-out is post-hoc and does not prove benefit. The design lesson is to show the decision boundary.'

    # 16 - qualitative
    $s = New-Slide $pres $false; Add-Title $s 'Written answers reveal what people need beyond the model' $false 'QUALITATIVE RESULTS | 1,500 ANSWERS'
    $qual=@(
        @('40%','wanted academic engagement information','attendance, current enrolment'),
        @('26%','wanted personal circumstances','work, family, caring responsibilities'),
        @('76%','suggested a concrete next step','71% profiles; 82% charts'),
        @('2.8%','asserted an unsupported cause','association was usually treated cautiously')
    )
    for($i=0;$i -lt 4;$i++) {
        $x=55+($i%2)*440; $y=120+[Math]::Floor($i/2)*150
        Add-Box $s $x $y 410 122 $WHITE $(if($i -eq 3){$GOLD}else{$SOFTBLUE}) 8 1.3 | Out-Null
        Add-Text $s $qual[$i][0] ($x+18) ($y+19) 95 35 26 $(if($i -eq 3){$GOLD}else{$TEAL}) $true 2 | Out-Null
        Add-Text $s $qual[$i][1] ($x+122) ($y+17) 266 42 15 $NAVY $true | Out-Null
        Add-Text $s $qual[$i][2] ($x+122) ($y+67) 266 32 11 $MIDGREY $false | Out-Null
    }
    Add-Text $s 'Single coding pass; inter-coder agreement was not measured.' 70 432 820 25 13 $MUTEDRED $true 2 | Out-Null
    Add-Footer $s 16 $false
    Add-Notes $s 'Timing: 1:20. Focus on missing contextual information. Disclose the single coding pass and that comments were written, not spoken.'

    # 17 - boundaries
    $s = New-Slide $pres $false; Add-Title $s 'The evidence supports further validation - not deployment' $false 'SENSITIVITY AND LIMITATIONS'
    $left=@('Admission-time ROC-AUC fell to 0.874','Removing protected attributes changed 5 of 108 flags','Gender recall gap narrowed from 0.19 to 0.10','Enrolled-student sensitivity altered cohort rankings')
    Add-Box $s 52 118 405 322 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s 'What the checks show' 72 140 365 28 18 $TEAL $true | Out-Null
    Add-Bullets $s $left 74 185 350 220 14 $CHARCOAL $TEAL
    $right=@('One Portuguese institution','One fixed split and one locked test','Human volunteers, not support officers','No causal intervention or operational-benefit evidence','Subgroup results are descriptive - not a fairness certificate')
    Add-Box $s 503 118 405 322 $WHITE $SOFTBLUE 8 1.3 | Out-Null
    Add-Text $s 'What the checks cannot establish' 523 140 365 28 18 $GOLD $true | Out-Null
    Add-Bullets $s $right 525 185 350 220 14 $CHARCOAL $GOLD
    Add-Footer $s 17 $false
    Add-Notes $s 'Timing: 1:35. Be precise: protected-attribute analysis is descriptive. The system has not been externally, temporally, operationally or legally validated.'

    # 18 - conclusion (dark)
    $s = New-Slide $pres $true; Add-Title $s 'A transparent model is the better candidate for the next study' $true 'CONCLUSION'
    $conclusions=@(
        @('1','Predictive value','TabICL''s advantage over EBM and XGBoost was within paired-bootstrap uncertainty.'),
        @('2','Trustworthiness','SHAP was faithful, but the exact top reasons were often unstable and mostly restated progress.'),
        @('3','Human evidence','The study found no evidence that charts improved predictions; one chart invited over-reading.')
    )
    for($i=0;$i -lt 3;$i++) {
        $y=116+$i*102
        $o=$s.Shapes.AddShape($msoShapeOval,65,$y,48,48); $o.Fill.ForeColor.RGB=$(if($i -eq 2){$GOLD}else{$TEAL}); $o.Line.Visible=$msoFalse
        Add-Text $s $conclusions[$i][0] 65 ($y+8) 48 26 18 $NAVY $true 2 | Out-Null
        Add-Text $s $conclusions[$i][1] 135 ($y-2) 230 28 17 $WHITE $true | Out-Null
        Add-Text $s $conclusions[$i][2] 135 ($y+29) 750 42 13 0xE8E5E2 $false | Out-Null
    }
    Add-Box $s 85 430 790 54 0x684526 $GOLD 8 1.5 | Out-Null
    Add-Text $s 'Next step: validate an EBM-based contact-list tool with current cohorts and practising support staff.' 105 445 750 24 15 $GOLD $true 2 | Out-Null
    Add-Footer $s 18 $true 'AIT XDS | Questions'
    Add-Notes $s 'Timing: 1:10. Answer each RQ and end with the next validation step. Invite questions. Total planned speaking time: approximately 24-25 minutes.'

    # 19 - appendix divider
    $s = New-Slide $pres $true
    Add-Text $s 'Backup evidence' 80 170 800 60 36 $WHITE $true 2 | Out-Null
    Add-Text $s 'Detailed tables, sensitivity analyses, interface and reproducibility' 100 252 760 38 18 $GOLD $false 2 | Out-Null
    Add-Footer $s 19 $true 'APPENDIX'

    # 20 - detailed model table
    $s = New-Slide $pres $false; Add-Title $s 'Locked final-test model metrics' $false 'BACKUP'
    $rows=[object[][]]@(
        @('Model','ROC-AUC','Brier','Bal. acc.','Macro F1','Recall','Precision'),
        @('Logistic regression','0.953','0.082','0.752','0.766','0.507','0.991'),
        @('Decision tree','0.910','0.100','0.748','0.762','0.502','0.982'),
        @('XGBoost','0.956','0.071','0.752','0.766','0.507','0.991'),
        @('EBM','0.954','0.077','0.756','0.771','0.512','1.000'),
        @('TabICL','0.957','0.074','0.752','0.766','0.507','0.991')
    )
    Add-Table $s $rows 48 124 864 285 14 $NAVY $WHITE @(25,12,12,12,12,12,15) | Out-Null
    Add-Text $s 'All models flag the top 20%; recall and precision refer to dropout at that capacity.' 60 435 840 25 13 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 20 $false 'BACKUP | SOURCE: tables/final_test/metrics.csv'

    # 21 - paired comparisons
    $s = New-Slide $pres $false; Add-Title $s 'TabICL paired comparisons' $false 'BACKUP | 2,000 BOOTSTRAP RESAMPLES'
    $rows=[object[][]]@(
        @('Baseline','Delta ROC-AUC [95% CI]','Delta Brier [95% CI]','Interpretation'),
        @('Logistic regression','0.004 [-0.005, 0.014]','-0.008 [-0.017, 0.001]','Uncertain'),
        @('Decision tree','0.047 [0.029, 0.067]','-0.026 [-0.036, -0.016]','TabICL better'),
        @('XGBoost','0.001 [-0.006, 0.009]','0.003 [-0.003, 0.009]','Uncertain'),
        @('EBM','0.003 [-0.007, 0.014]','-0.003 [-0.010, 0.004]','Uncertain')
    )
    Add-Table $s $rows 48 132 864 250 14 $NAVY $WHITE @(22,29,29,20) | Out-Null
    Add-Text $s 'Differences are TabICL minus baseline; lower Brier is better.' 60 414 840 25 13 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 21 $false 'BACKUP | SOURCE: tables/final_test/paired_comparisons.csv'

    # 22 - EDA table
    $s = New-Slide $pres $false; Add-Title $s 'Training-split profile by outcome' $false 'BACKUP | n = 2,541'
    $rows=[object[][]]@(
        @('Characteristic','Dropout','Graduate'),
        @('Students','995','1,546'),
        @('First-semester units passed (mean)','2.6','6.3'),
        @('Passed no first-semester unit','39.6%','3.2%'),
        @('Took no first-semester evaluation','17.6%','3.0%'),
        @('Average grade (mean)','7.3','12.7'),
        @('Tuition fees up to date','68.7%','98.6%'),
        @('Debtor','21.5%','5.0%'),
        @('Scholarship holder','9.8%','39.1%'),
        @('Age at enrolment (median)','23','19'),
        @('Female','52.4%','77.0%')
    )
    Add-Table $s $rows 110 110 740 350 12 $NAVY $WHITE @(60,20,20) | Out-Null
    Add-Footer $s 22 $false 'BACKUP | TRAINING DATA ONLY'

    # 23 - explanation evidence images
    $s = New-Slide $pres $false; Add-Title $s 'Deletion faithfulness and pairwise effects' $false 'BACKUP | VALIDATION'
    Add-PictureFit $s 'W1_analysis\03_Full_Audit\Figures\deletion_faithfulness_validation.png' 48 112 425 305 $true | Out-Null
    Add-PictureFit $s 'W1_analysis\03_Full_Audit\Figures\pairwise_reference_masking_validation.png' 487 112 425 305 $true | Out-Null
    Add-Text $s 'Deletion test: 536 of 544 cases had positive faithfulness area.' 55 432 410 32 12 $CHARCOAL $true 2 | Out-Null
    Add-Text $s 'Progress x participation was the largest common non-additive pair.' 494 432 410 32 12 $CHARCOAL $true 2 | Out-Null
    Add-Footer $s 23 $false 'BACKUP | EXPLANATION AUDIT'

    # 24 - sensitivity table
    $s = New-Slide $pres $false; Add-Title $s 'Validation sensitivity analyses' $false 'BACKUP | EXPLORATORY'
    $rows=[object[][]]@(
        @('Setting','ROC-AUC','Brier','Recall@20%','Precision@20%'),
        @('Primary: after S1','0.952','0.071','0.507','1.000'),
        @('Admission-time window','0.874','0.135','0.469','0.926'),
        @('Without protected attributes','0.950','0.072','0.507','1.000'),
        @('Enrolled added: frozen model','0.924','0.111','0.587','0.947'),
        @('Enrolled added: grouped refit','0.929','0.085','0.606','0.977'),
        @('At least 1 evaluation; re-ranked','0.949','--','0.559','1.000')
    )
    Add-Table $s $rows 55 122 850 300 13 $NAVY $WHITE @(40,15,15,15,15) | Out-Null
    Add-Text $s 'Not used for model selection; Enrolled is treated as non-dropout only for this grouped sensitivity.' 70 447 820 28 12 $MIDGREY $false 2 | Out-Null
    Add-Footer $s 24 $false 'BACKUP | SENSITIVITY'

    # 25 - subgroup table
    $s = New-Slide $pres $false; Add-Title $s 'Descriptive subgroup diagnostics' $false 'BACKUP | NOT A FAIRNESS CERTIFICATE'
    $rows=[object[][]]@(
        @('Attribute','Group','n','Dropout rate','Flag rate','Recall'),
        @('Gender','Female','335','0.299','0.122','0.410'),
        @('Gender','Male','210','0.538','0.324','0.593'),
        @('Displaced','No','229','0.476','0.288','0.596'),
        @('Displaced','Yes','316','0.329','0.136','0.414'),
        @('Age at entry','<=20','318','0.283','0.116','0.411'),
        @('Age at entry','21-25','93','0.430','0.194','0.450'),
        @('Age at entry','26-35','83','0.663','0.434','0.655'),
        @('Age at entry','36+','51','0.549','0.353','0.607')
    )
    Add-Table $s $rows 70 118 820 325 13 $NAVY $WHITE @(23,15,10,18,16,18) | Out-Null
    Add-Footer $s 25 $false 'BACKUP | LOCKED FINAL TEST'

    # 26 - human detail
    $s = New-Slide $pres $false; Add-Title $s 'Human-study case and confidence detail' $false 'BACKUP'
    Add-PictureFit $s 'figures\human_study\human_confidence_vs_accuracy.png' 45 112 420 320 $true | Out-Null
    Add-PictureFit $s 'figures\human_study\human_completion_time.png' 495 112 420 320 $true | Out-Null
    Add-Text $s 'Chart group: higher mean confidence without higher accuracy.' 55 446 400 25 12 $CHARCOAL $true 2 | Out-Null
    Add-Text $s 'Self-reported time difference: -3.2 min [-8.7, 2.0].' 505 446 400 25 12 $CHARCOAL $true 2 | Out-Null
    Add-Footer $s 26 $false 'BACKUP | HUMAN STUDY'

    # 27 - qualitative table
    $s = New-Slide $pres $false; Add-Title $s 'Primary qualitative themes' $false 'BACKUP | SINGLE CODING PASS'
    $rows=[object[][]]@(
        @('Question','Theme','Share'),
        @('Why flagged','Explanation chart','36.0%'),
        @('Why flagged','Academic evidence','31.0%'),
        @('Why flagged','Several factors','28.0%'),
        @('Suggested support','Academic support','29.8%'),
        @('Suggested support','No action','21.0%'),
        @('Suggested support','Advising / monitoring','16.0%'),
        @('Suggested support','Financial / admin. support','15.2%'),
        @('Missing information','Academic engagement','39.8%'),
        @('Missing information','Personal circumstances','25.8%')
    )
    Add-Table $s $rows 115 112 730 350 12 $NAVY $WHITE @(31,49,20) | Out-Null
    Add-Footer $s 27 $false 'BACKUP | 1,500 WRITTEN ANSWERS'

    # 28 - interface
    $s = New-Slide $pres $false; Add-Title $s 'Local research interface demonstration' $false 'BACKUP | VALIDATION ONLY'
    Add-PictureFit $s 'Final_Report\figures\interface_validation_916.png' 42 110 420 345 $true | Out-Null
    Add-PictureFit $s 'Final_Report\figures\interface_whatif_174.png' 498 110 420 345 $true | Out-Null
    Add-Text $s 'Saved view: flag, rank, reasons and stability' 55 463 395 22 11 $CHARCOAL $true 2 | Out-Null
    Add-Text $s 'What-if: model response, not causal advice' 510 463 395 22 11 $CHARCOAL $true 2 | Out-Null
    Add-Footer $s 28 $false 'BACKUP | DEMONSTRATION, NOT USER-TESTED'

    # 29 - contributions
    $s = New-Slide $pres $false; Add-Title $s 'Team contributions' $false 'BACKUP'
    $rows=[object[][]]@(
        @('Member','Main contribution'),
        @('Yolanda Lim','Pipeline, frozen test, human analysis, sensitivity, interface, integration'),
        @('Lucas Nguyen','Assignment generator, chart/profile renderer, tests and documentation'),
        @('Noey Theppithuk','Data/model audits and full explanation audit'),
        @('Han Zaw','Forms, case-pack contract, response transformation and export checks'),
        @('Harry Han','Ethics materials, recruitment, pilot, send log and collection'),
        @('All members','Recruitment, report and presentation')
    )
    Add-Table $s $rows 58 120 844 310 13 $NAVY $WHITE @(26,74) | Out-Null
    Add-Footer $s 29 $false 'BACKUP | TEAM'

    # 30 - reproducibility
    $s = New-Slide $pres $false; Add-Title $s 'Reproducibility and provenance' $false 'BACKUP'
    Add-KPI $s 'Once' 'Locked final-test execution on 2 November 2026' 55 120 250 $TEAL
    Add-KPI $s '98' 'Automated unit tests in the release check' 355 120 250 $GOLD
    Add-KPI $s 'Seed 42' 'Frozen split and analysis seeds' 655 120 250 $TEAL
    Add-Bullets $s @('Split IDs, protocol, code snapshot and fitted model were hashed','Report assets regenerate from saved aggregates without refitting','Raw participant responses are intentionally not shared','Release readiness verifies paths, numbers and documentation') 80 285 800 160 15 $CHARCOAL $TEAL
    Add-Footer $s 30 $false 'BACKUP | REPRODUCIBILITY'

    # Document properties
    try {
        $pres.BuiltInDocumentProperties.Item('Title').Value = 'Evaluating the Trustworthiness of Explanations for Student Dropout Risk: Comparing Black-Box and Interpretable Models'
        $pres.BuiltInDocumentProperties.Item('Author').Value = 'The Interpreters'
        $pres.BuiltInDocumentProperties.Item('Subject').Value = 'AIT XDS final project presentation'
        $pres.BuiltInDocumentProperties.Item('Comments').Value = 'Editable 25-minute presentation generated from the final report and report-ready aggregate evidence.'
    } catch { }

    $pres.SaveAs($OutputPath, $ppSaveAsOpenXMLPresentation)
    $pdfPath = [System.IO.Path]::ChangeExtension($OutputPath, '.pdf')
    $pres.SaveAs($pdfPath, $ppSaveAsPDF)
    Write-Output "PPTX=$OutputPath"
    Write-Output "PDF=$pdfPath"
    Write-Output "Slides=$($pres.Slides.Count)"
}
finally {
    if ($pres) { try { $pres.Close() } catch { } }
    if ($ppt) { try { $ppt.Quit() } catch { } }
    if ($pres) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null }
    if ($ppt) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
