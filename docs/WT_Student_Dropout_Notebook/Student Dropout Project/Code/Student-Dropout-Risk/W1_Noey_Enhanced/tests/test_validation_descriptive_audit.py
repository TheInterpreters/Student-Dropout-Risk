import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validation_descriptive_audit import observed_groups, validation_only

class DescriptiveAuditTests(unittest.TestCase):
    def test_actual_outcomes_only_validation(self):
        data=pd.DataFrame({'Marital status':[1,1,2,2],'Curricular units 1st sem (grade)':[9,13,11,8],
                           'Curricular units 1st sem (enrolled)':[6]*4,'Curricular units 1st sem (approved)':[1,5,4,0],
                           'Tuition fees up to date':[0,1,1,0],'Debtor':[1,0,0,1],
                           'Target':['Dropout','Graduate','Graduate','Enrolled']})
        splits=pd.DataFrame({'source_row_id':[0,1,2],'split':['validation','train','test']})
        validation=validation_only(data,splits)
        self.assertEqual(validation.source_row_id.tolist(),[0])
        audit=observed_groups(validation)
        first=audit.iloc[0]
        self.assertEqual(first['n'],1)
        self.assertEqual(first['dropouts'],1)
        self.assertEqual(first['observed_dropout_rate_pct'],100)
    def test_reject_missing_split(self):
        data=pd.DataFrame({'Target':['Dropout','Graduate']})
        splits=pd.DataFrame({'source_row_id':[0],'split':['validation']})
        with self.assertRaises(ValueError):validation_only(data,splits)

if __name__=='__main__':unittest.main()
