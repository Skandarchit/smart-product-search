import importlib.util
from pathlib import Path
import unittest

@unittest.skipUnless(importlib.util.find_spec('streamlit'),'Optional Streamlit not installed')
class UITests(unittest.TestCase):
    def test_shopping_journey(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.json)
        self.assertNotIn('Search method',[x.label for x in app.selectbox])
        app.text_input(key='shop_query_retail').set_value('alarm clock')
        app.button(key='find_products').click().run()
        engine=app.session_state['shop_engine']
        self.assertEqual(engine.catalog.terms['alarm clock'],1)
        app.run();self.assertEqual(engine.catalog.terms['alarm clock'],1)
        adds=[b for b in app.button if b.key.startswith('shop_add_')]
        self.assertEqual(len(adds),5)
        pid=adds[0].key.removeprefix('shop_add_');adds[0].click().run()
        self.assertEqual(app.session_state['shopping_carts']['retail'][pid],1)
        self.assertEqual(engine.catalog.terms['alarm clock'],1)
        app.button(key='shop_view_'+pid).click().run()
        self.assertEqual(app.session_state['selected_retail'],pid);self.assertFalse(app.exception)
        app.button(key='detail_add').click().run()
        app.radio(key='shop_page').set_value('My cart').run()
        self.assertEqual(app.number_input(key='quantity_retail_'+pid).value,2)
        app.number_input(key='quantity_retail_'+pid).set_value(3).run()
        app.text_input(key='offer_code').set_value('SAVE5').run()
        self.assertFalse(app.json);self.assertTrue(any('Offer applied' in x.value for x in app.success))
        self.assertEqual(app.session_state['shopping_carts']['retail'][pid],3)
        app.radio(key='shop_page').set_value('Store overview').run();self.assertFalse(app.exception)
        self.assertEqual(app.dataframe[0].value.iloc[0]['Times searched'],1)
        app.radio(key='shop_page').set_value('Shop').run()
        app.selectbox(key='shop_collection').set_value('Everyday essentials · ₹').run()
        self.assertEqual(app.session_state['shopping_carts']['teaching'],{})
        app.text_input(key='shop_query_teaching').set_value('phone')
        app.number_input(key='shop_budget_teaching').set_value(2000)
        app.button(key='find_products').click().run()
        self.assertFalse(app.exception)
        self.assertTrue([b for b in app.button if b.key.startswith('shop_add_')])
        app.radio(key='shop_page').set_value('Coursework').run();self.assertFalse(app.exception)
        app.selectbox(key='lab_page').set_value('Learning lab').run();self.assertFalse(app.exception)
        app.selectbox(key='shop_collection').set_value('Home & gifts · £').run()
        app.radio(key='shop_page').set_value('My cart').run()
        self.assertEqual(app.session_state['shopping_carts']['retail'][pid],3)
        app.button(key='remove_'+pid).click().run();self.assertFalse(app.exception)
        self.assertEqual(app.session_state['shopping_carts']['retail'],{})

if __name__=='__main__':unittest.main()
