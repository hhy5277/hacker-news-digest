#coding: utf-8
import os.path
import logging
import unittest
from unittest import TestCase
import tempfile

from bs4 import BeautifulSoup as BS
from page_content_extractor import *
from page_content_extractor.html import *

class PageContentExtractorTestCase(TestCase):

    def test_purge(self):
        html_doc = """
        <html>good<script>whatever</script></html>
        """
        doc = BS(html_doc)
        HtmlContentExtractor.purge.im_func(object(), doc)
        self.assertIsNone(doc.find('script'))

    def test_text_len_with_comma(self):
        html_doc = u"""
        <html>good,，</html>
        """
        with tempfile.NamedTemporaryFile() as fd:
            fd.write(html_doc.encode('utf-8'))
            fd.seek(0)
            resp = urllib2.urlopen('file://%s' % fd.name)
            doc = BS(html_doc, from_encoding='utf-8')
            length = HtmlContentExtractor(resp).text_len(doc)
            self.assertEqual(length, 8)

    def test_parsing_empty_response(self):
        html_doc = u"""
        """
        with tempfile.NamedTemporaryFile() as fd:
            fd.write(html_doc.encode('utf-8'))
            fd.seek(0)
            resp = urllib2.urlopen('file://%s' % fd.name)
            self.assertEqual(HtmlContentExtractor(resp).article.text, '')

    def test_summary_with_no_first_header(self):
        html_doc = u"""
        <p>1<h1>2</h1><div>3</div><h1>4</h1></p>
        """
        with tempfile.NamedTemporaryFile() as fd:
            fd.write(html_doc.encode('utf-8'))
            fd.seek(0)
            resp = urllib2.urlopen('file://%s' % fd.name)
            self.assertEqual(HtmlContentExtractor(resp).get_summary(), '1 3 4')

    def test_semantic_affect(self):
        assert HtmlContentExtractor.semantic_effect.im_func(object(),
                BS('<article>good</article>').article) == 2
        assert HtmlContentExtractor.semantic_effect.im_func(object(),
                BS('<p>good</p>').p) == 1
        assert HtmlContentExtractor.semantic_effect.im_func(object(),
                BS('<p class="conteNt">good</p>').p) == 2
        assert HtmlContentExtractor.semantic_effect.im_func(object(),
                BS('<p class="comment">good</p>').p) == .2

    def test_check_image(self):
        html_doc = """
        <img src="http://img3.douban.com/view/event_poster/raw/public/38c9a52fb4c13fd.jpg" />
        """
        img = WebImage('http://www.douban.com/', BS(html_doc).img)
        print img.is_possible

    def test_simple_page_extract(self):
        e = legendary_parser_factory('http://www.infzm.com/content/81698')
        print e.get_summary()
        # e.get_top_image().save('/tmp/downimg')

    def test_clean_up_html_not_modify_iter_while_looping(self):
        resp = urllib2.urlopen('file://%s' % os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'fixtures/kim.com.html'))
        try:
            HtmlContentExtractor(resp)
        except AttributeError as e:
            self.fail('%s, maybe delete something while looping.' % e)
        

if __name__ == '__main__':
    # basicConfig will only be called automatically when calling
    # logging.debug, logging.info ...
    # calling those method against a logger instance won't apply the basic config
    # see https://docs.python.org/2/library/logging.html#logging.basicConfig
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - [%(asctime)s] %(message)s')
    unittest.main()
