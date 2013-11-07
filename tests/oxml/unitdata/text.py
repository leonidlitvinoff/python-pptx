# encoding: utf-8

"""
XML test data builders for pptx.oxml.text unit tests
"""

from pptx.oxml import parse_xml_bytes
from pptx.oxml.ns import nsdecls


class BaseBuilder(object):
    """
    Provides common behavior for all data builders.
    """
    def __init__(self):
        self._empty = False
        self._nsdecls = ''
        self._xmlattrs = {}
        self._xmlattr_method_map = {}
        for xmlattr_name in self.__attrs__:
            self._xmlattrs[xmlattr_name] = ''
            method_name = 'with_%s' % xmlattr_name
            self._xmlattr_method_map[method_name] = xmlattr_name
        self._child_bldrs = []

    def __getattr__(self, name):
        """
        Intercept attribute access to generalize "with_{xmlattr_name}()"
        methods.
        """
        if name in self._xmlattr_method_map:
            def with_xmlattr(value):
                xmlattr_name = self._xmlattr_method_map[name]
                self._set_xmlattr(xmlattr_name, value)
                return self
            return with_xmlattr
        else:
            tmpl = "'%s' object has no attribute '%s'"
            raise AttributeError(tmpl % (self.__class__.__name__, name))

    @property
    def element(self):
        """Return element based on XML generated by builder"""
        elm = parse_xml_bytes(self.xml())
        return elm

    def with_child(self, child_bldr):
        self._child_bldrs.append(child_bldr)
        return self

    def with_nsdecls(self):
        self._nsdecls = ' %s' % nsdecls(*self.__nspfxs__)
        return self

    def xml(self, indent=0):
        """
        Return element XML based on attribute settings
        """
        indent_str = ' ' * indent
        if self._is_empty:
            xml = '%s%s\n' % (indent_str, self._empty_element_tag)
        else:
            xml = '%s\n' % self._non_empty_element_xml(indent)
        return xml

    def xml_bytes(self, indent=0):
        return self.xml(indent=indent).encode('utf-8')

    @property
    def _empty_element_tag(self):
        return '<%s%s%s/>' % (self.__tag__, self._nsdecls, self._xmlattrs_str)

    @property
    def _end_tag(self):
        return '</%s>' % self.__tag__

    @property
    def _is_empty(self):
        return len(self._child_bldrs) == 0

    def _non_empty_element_xml(self, indent):
        indent_str = ' ' * indent
        xml = '%s%s\n' % (indent_str, self._start_tag)
        for child_bldr in self._child_bldrs:
            xml += child_bldr.xml(indent+2)
        xml += '%s%s' % (indent_str, self._end_tag)
        return xml

    def _set_xmlattr(self, xmlattr_name, value):
        xmlattr_str = ' %s="%s"' % (xmlattr_name, str(value))
        self._xmlattrs[xmlattr_name] = xmlattr_str

    @property
    def _start_tag(self):
        return '<%s%s%s>' % (self.__tag__, self._nsdecls, self._xmlattrs_str)

    @property
    def _xmlattrs_str(self):
        """
        Return all element attributes as a string, like ' foo="bar" x="1"'.
        """
        xmlattrs_str = ''
        for xmlattr_name in sorted(self._xmlattrs.keys()):
            xmlattrs_str += self._xmlattrs[xmlattr_name]
        return xmlattrs_str


class CT_OfficeArtExtensionList(BaseBuilder):
    __tag__ = 'a:extLst'
    __nspfxs__ = ('a',)
    __attrs__ = ()


def an_extLst():
    return CT_OfficeArtExtensionList()


class CT_RegularTextRunBuilder(BaseBuilder):
    __tag__ = 'a:r'
    __nspfxs__ = ('a',)
    __attrs__ = ()


def an_r():
    return CT_RegularTextRunBuilder()


class CT_TextCharacterPropertiesBuilder(BaseBuilder):
    """
    Test data builder for CT_TextCharacterProperties XML element that appears
    as <a:endParaRPr> child of <a:p> and <a:rPr> child of <a:r>.
    """
    __nspfxs__ = ('a',)
    __attrs__ = ('b', 'i', 'sz', 'u')

    def __init__(self, tag):
        self.__tag__ = tag
        super(CT_TextCharacterPropertiesBuilder, self).__init__()


def a_defRPr():
    return CT_TextCharacterPropertiesBuilder('a:defRPr')


def an_endParaRPr():
    return CT_TextCharacterPropertiesBuilder('a:endParaRPr')


def an_rPr():
    return CT_TextCharacterPropertiesBuilder('a:rPr')


class CT_TextParagraphBuilder(BaseBuilder):
    """
    Test data builder for CT_TextParagraph (<a:p>) XML element that appears
    as a child of <p:txBody>.
    """
    __tag__ = 'a:p'
    __nspfxs__ = ('a',)
    __attrs__ = ()


def a_p():
    """Return a CT_TextParagraphBuilder instance"""
    return CT_TextParagraphBuilder()


class CT_TextParagraphPropertiesBuilder(BaseBuilder):
    """
    Test data builder for CT_TextParagraphProperties (<a:pPr>) XML element
    that appears as a child of <a:p>.
    """
    __tag__ = 'a:pPr'
    __nspfxs__ = ('a',)
    __attrs__ = (
        'marL', 'marR', 'lvl', 'indent', 'algn', 'defTabSz', 'rtl',
        'eaLnBrk', 'fontAlgn', 'latinLnBrk', 'hangingPunct'
    )


def a_pPr():
    """Return a CT_TextParagraphPropertiesBuilder instance"""
    return CT_TextParagraphPropertiesBuilder()


class XsdString(BaseBuilder):
    __attrs__ = ()

    def __init__(self, tag, nspfxs):
        self.__tag__ = tag
        self.__nspfxs__ = nspfxs
        super(XsdString, self).__init__()


def a_t():
    return XsdString('a:t', ('a',))
