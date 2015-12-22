from django import test

from .. import forms


class FormForTest(forms.Form):
    user = forms.CharField(required=True)
    password = forms.CharField(required=True)


class FormTest(test.TestCase):

    def test_basic_validation(self):
        form = FormForTest(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            len(form.errors['user']),
            1
        )
        self.assertIsInstance(
            form.errors['user'][0],
            forms.exceptions.ValidationError
        )
        self.assertEqual(
            form.errors['user'][0].code,
            forms.exceptions.VALIDATION_REQUIRED
        )
        self.assertEqual(
            len(form.errors['password']),
            1
        )
        self.assertIsInstance(
            form.errors['password'][0],
            forms.exceptions.ValidationError
        )

    def test_advanced_validation(self):
        data = {'user': 'ilya', 'password': '123', }
        form = FormForTest(data=data)
        self.assertTrue(form.is_valid())
        self.assertDictEqual(
            form.cleaned_data,
            data
        )

    def test_char_field(self):
        class F(forms.Form):
            wow = forms.CharField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 123}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )

    def test_int_field(self):
        class F(forms.Form):
            wow = forms.IntegerField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 123}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "123"}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_decimal_field(self):
        class F(forms.Form):
            wow = forms.DecimalField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 123}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 123.123}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "123.123"}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_date_field(self):
        class F(forms.Form):
            wow = forms.DateField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': ""}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 25}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "2014-12-01"}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_time_field(self):
        class F(forms.Form):
            wow = forms.TimeField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': ""}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 25}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "12:30:23"}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "12:30"}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_choice_field(self):
        class F(forms.Form):
            wow = forms.ChoiceField(choices=(1, 2, 3), required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': ""}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 25}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 0}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 1}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 2}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 3}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 4}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_boolean_field(self):
        class F(forms.Form):
            wow = forms.BooleanField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': ""}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 25}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': True}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': False}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_array_field(self):
        class F(forms.Form):
            wow = forms.ArrayField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': ""}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 25}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': []}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "[1,3,4,5]"}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "(1,3,4,5)"}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "1,3,4,5"}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_int_array_field(self):
        class F(forms.Form):
            wow = forms.IntArrayField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 25}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': []}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "[1,3,4,5]"}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "(1,3,4,5)"}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': "1,3,4,5"}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asdasd'}).is_valid()
        )

    def test_dict_array_field(self):
        class Villain(forms.Form):
            name = forms.CharField()
            age = forms.IntegerField(min_value=5, required=True)

        class F(forms.Form):
            wow = forms.DictArrayField(
                required=True,
                form=Villain,
                min_length=1
            )

        good_data = [
            {
                "wow": [{
                    "name": "dr. Evil",
                    "age": 12
                }]
            },
            {
                "wow": [{
                    "name": "",
                    "age": 6
                }]
            },
            {
                "wow": [{
                    "age": 12
                }]
            },
        ]
        bad_data = [
            {},
            {
                "wow": []
            },
            {
                "wow": [{}]
            },
            {
                "wow": [{
                    "age": 3
                }]
            },
        ]

        print 'good'
        for data in good_data:
            print data
            self.assertTrue(
                F(data=data).is_valid()
            )

        print 'bad'
        for data in bad_data:
            print data
            self.assertFalse(
                F(data=data).is_valid()
            )

    def test_dict_field(self):
        class Villain(forms.Form):
            name = forms.CharField()
            age = forms.IntegerField(min_value=5, required=True)

        class F(forms.Form):
            wow = forms.DictField(
                required=True,
                form=Villain,
                min_length=1
            )

        good_data = [
            {
                "wow": {
                    "name": "dr. Evil",
                    "age": 12
                }
            },
            {
                "wow": {
                    "name": "",
                    "age": 6
                }
            },
            {
                "wow": {
                    "age": 12
                }
            },
        ]
        bad_data = [
            {},
            {
                "wow": {}
            },
            {
                "wow": {}
            },
            {
                "wow": {
                    "age": 3
                }
            },
        ]

        print 'good'
        for data in good_data:
            print data
            self.assertTrue(
                F(data=data).is_valid()
            )

        print 'bad'
        for data in bad_data:
            print data
            self.assertFalse(
                F(data=data).is_valid()
            )

    def test_email_field(self):
        class F(forms.Form):
            wow = forms.EmailField(required=True)

        self.assertFalse(
            F(data={}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 123}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asd@'}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': 'asd@asd'}).is_valid()
        )
        self.assertTrue(
            F(data={'wow': 'asd@asd.sd'}).is_valid()
        )
        self.assertFalse(
            F(data={'wow': None}).is_valid()
        )
