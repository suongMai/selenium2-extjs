'''
'''
from selenium2extjs.webelements.ExtJSWebElement import ExtJSWebElement
from selenium2extjs.webelements import ExtJSQueryType


FUNCTION_DEFINE_MyExt = '''
    if (typeof MyExt === "undefined") {
        MyExt = function() {
        };
        MyExt.log = function(arg) {
            if (console && console.log)
                console.log(arg)
        }
    };
'''

FUNCTION_findVisibleComponentElement = '''
    MyExt.findVisibleComponentElement = function(query) {
        var queryResultArray = (window.frames[0] && window.frames[0].Ext) ? 
                window.frames[0].Ext.ComponentQuery.query(query)
                : Ext.ComponentQuery.query(query);
        var single = null;
        Ext.Array.every(queryResultArray, function(comp) {
            if (comp != null && comp.isVisible(true)) {
                single = comp;
            }
            return (single != null);
        });
        var el = (single != null ? single.getEl().dom : null);
        return el;
    }
'''

FUNCTION_getXPathTo = '''
    MyExt.getXPathTo = function getXPathTo(element) {
        if (element.id !== '')
            return 'id("' + element.id + '")';
        if (element === document.body)
            return element.tagName;
        var ix = 0;
        var siblings = element.parentNode.childNodes;
        for (var i = 0; i < siblings.length; i++) {
            var sibling = siblings[i];
            if (sibling === element)
                return MyExt.getXPathTo(element.parentNode) + '/' + element.tagName
                        + '[' + (ix + 1) + ']';
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                ix++;
        }
    }
'''

SCRIPT_TOP_ELEMENT_TO_EXT_JS_CMP = '''
    var id = el.id.replace(/-\w*El$/, '').replace('-triggerWrap', '');
    var extCmp = Ext.getCmp(el.id);
'''

SCRIPT_QUERY_CMP = '''
    %s;
    %s;
    return MyExt.findVisibleComponentElement("%s");
'''

SCRIPT_GET_CMP = '''
    return Ext.getCmp("%s").getEl().dom;
'''

# need to handle is xtype to return the Id on GUI
SCRIPT_TOP_ELEMENT_TO_EXT_JS_ID = '''
    %s;
    return extCmp.id;
''' % SCRIPT_TOP_ELEMENT_TO_EXT_JS_CMP


class ExtJSComponent(ExtJSWebElement):
    '''
    '''

    def __init__(self, driver, query_type="", query="", top_element=None):
        '''
        Constructor
        '''
        if query_type and query:
            super(ExtJSComponent, self).__init__(
                driver=driver,
                js_code=self.convert_query_type_and_query_to_script(
                    query_type, query
                )
            )

            self.ext_js_cmp_id = None
            if query_type == ExtJSQueryType.GetCmp:
                self.ext_js_cmp_id = query

        if top_element:
            super(ExtJSComponent, self).__init__(
                driver=driver, top_element=top_element)

    def convert_query_type_and_query_to_script(self, query_type, query):
        query_script = None

        if query_type == ExtJSQueryType.ComponentQuery:
            query_script = SCRIPT_QUERY_CMP % (
                FUNCTION_DEFINE_MyExt,
                FUNCTION_findVisibleComponentElement, query
            )

        elif query_type == ExtJSQueryType.GetCmp:
            SCRIPT_GET_CMP % (query)

        elif query_type == ExtJSQueryType.Custom:
            query_script = query

        return query_script

    def get_el_dom(self):
        return self.exec_script_on_ext_js_cmp("return extCmp.getEl().dom")

    def get_component_id(self):
        '''to get Component id by query'''
        if self.ext_js_cmp_id is None:
            # well then we better have the WebElement!
            if self.top_element is None:
                raise("Neither extJsCmpId or topElement has been set")

            self.ext_js_cmp_id = self.exec_script_on_top_level_element(
                SCRIPT_TOP_ELEMENT_TO_EXT_JS_ID)

        return self.ext_js_cmp_id

    '''This is used to run java scripts on
        the ExtJS ExtJSComponent.For Example:
             execScriptOnExtJsComponent("return extCmp.getValue()");
        will run theJavaScript method getValue on the ExtJS component object.
    '''

    def exec_script_on_ext_js_cmp(self, js_code):
        script = "var extCmp = Ext.getCmp('%s'); %s;"
        return self.exec_script_clean(script)

    def exec_script_on_ext_js_cmp_return_boolean(self, js_code):
        script = "var extCmp = Ext.getCmp('%s'); %s;" % (
            self.get_component_id(),
            js_code)

        return self.execScriptCleanReturnBoolean(script)

    def exec_script_clean_return_boolean(self, script):
        try:
            res = self.exec_script_clean(script)
            if res:
                return True

        except:
            return False

        return False

    '''
     Returns an XPath to the Ext component,
     which contains the ID provided by getId()
     @return String
     '''

    def get_xpath(self):
        return "%s return getPathTo(%s" % (FUNCTION_getXPathTo,
                                           self.top_element)

    def get_expression(self):
        return "window.Ext.getCmp('%s')" % self.get_component_id()
