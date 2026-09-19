import unittest

from src.modeling import (
    CATEGORICAL_COLUMNS,
    add_first_semester_features,
    feature_columns,
    load_primary_data,
    make_splits,
    prepare_tfm_frame,
)


class ModelingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = load_primary_data()

    def test_binary_target_and_enrolled_removed(self):
        self.assertEqual(set(self.frame["target"].unique()), {0, 1})

    def test_second_semester_never_enters_primary_window(self):
        columns = feature_columns(self.frame, "first_semester")
        self.assertFalse(any(column.startswith("curricular_units_2nd_sem") for column in columns))

    def test_enrollment_window_excludes_raw_and_derived_first_semester_fields(self):
        frame = add_first_semester_features(self.frame)
        columns = feature_columns(frame, "enrollment")
        self.assertFalse(any(column.startswith("curricular_units_1st_sem") for column in columns))
        self.assertFalse(any(column.startswith("first_semester_") for column in columns))

    def test_split_ids_are_disjoint_and_complete(self):
        splits = make_splits(self.frame)
        groups = [set(splits.train_ids), set(splits.validation_ids), set(splits.test_ids)]
        self.assertTrue(groups[0].isdisjoint(groups[1]))
        self.assertTrue(groups[0].isdisjoint(groups[2]))
        self.assertTrue(groups[1].isdisjoint(groups[2]))
        self.assertEqual(len(set.union(*groups)), len(self.frame))

    def test_tfm_frame_marks_coded_categories_as_categorical(self):
        frame = add_first_semester_features(self.frame)
        columns = feature_columns(frame)
        prepared = prepare_tfm_frame(frame.head(5), columns)
        eligible = set(columns).intersection(CATEGORICAL_COLUMNS)
        self.assertTrue(eligible)
        self.assertTrue(all(str(prepared[column].dtype) == "category" for column in eligible))


if __name__ == "__main__":
    unittest.main()
