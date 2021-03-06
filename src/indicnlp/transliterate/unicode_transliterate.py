# Copyright Anoop Kunchukuttan 2013 - present
#
# This file is part of Indic NLP Library.
# 
# Indic NLP Library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Indic NLP Library is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
# 
#        You should have received a copy of the GNU General Public License
#        along with Indic NLP Library.  If not, see <http://www.gnu.org/licenses/>.
#

#Program for text written in one Indic script to another based on Unicode mappings. 
#
# @author Anoop Kunchukuttan 
#

import sys, codecs, string, itertools, re

from indicnlp import langinfo 
from indicnlp.transliterate import itrans_transliterator

class UnicodeIndicTransliterator(object):
    """
    Base class for transliterator of Indian languages. 

    Script pair specific transliterators should derive from this class and override the transliterate() method. 
    They can call the super class 'transliterate()' method to avail of the common transliteration
    """

    @staticmethod
    def transliterate(text,lang1_code,lang2_code):
        if langinfo.SCRIPT_RANGES.has_key(lang1_code) and langinfo.SCRIPT_RANGES.has_key(lang2_code):
            trans_lit_text=[]
            for c in text: 
                newc=c
                offset=ord(c)-langinfo.SCRIPT_RANGES[lang1_code][0]
                if offset >=langinfo.COORDINATED_RANGE_START_INCLUSIVE and offset <= langinfo.COORDINATED_RANGE_END_INCLUSIVE:
                    # handle missing unaspirated and voiced plosives in Tamil script 
                    # replace by unvoiced, unaspirated plosives
                    if lang2_code=='ta' and offset>=0x15 and offset<=0x2E and (offset-0x15)%5!=0:
                        subst_char=(offset-0x15)/5
                        offset=0x15+5*subst_char
                    newc=unichr(langinfo.SCRIPT_RANGES[lang2_code][0]+offset)
                trans_lit_text.append(newc)        
            return string.join(trans_lit_text,sep='')
        else:
            return text

class ItransTransliterator(object):
    """
    Transliterator between Indian scripts and ITRANS
    """

    @staticmethod
    def to_itrans(text,lang_code):
        if langinfo.SCRIPT_RANGES.has_key(lang_code):
            if lang_code=='ml': 
                # Change from chillus characters to corresponding consonant+halant
                text=text.replace(u'\u0d7a',u'\u0d23\u0d4d')
                text=text.replace(u'\u0d7b',u'\u0d28\u0d4d')
                text=text.replace(u'\u0d7c',u'\u0d30\u0d4d')
                text=text.replace(u'\u0d7d',u'\u0d32\u0d4d')
                text=text.replace(u'\u0d7e',u'\u0d33\u0d4d')
                text=text.replace(u'\u0d7f',u'\u0d15\u0d4d')

            devnag=UnicodeIndicTransliterator.transliterate(text,lang_code,'hi')
            
            itrans=itrans_transliterator.transliterate(devnag.encode('utf-8'), 'devanagari','itrans',
                                 {'outputASCIIEncoded' : False, 'handleUnrecognised': itrans_transliterator.UNRECOGNISED_ECHO})
            return itrans.decode('utf-8') 
        else:
            return text

    @staticmethod
    def from_itrans(text,lang_code):
        if langinfo.SCRIPT_RANGES.has_key(lang_code): 
            devnag_text=itrans_transliterator.transliterate(text.encode('utf-8'), 'itrans', 'devanagari',
                                 {'outputASCIIEncoded' : False, 'handleUnrecognised': itrans_transliterator.UNRECOGNISED_ECHO})

            lang_text=UnicodeIndicTransliterator.transliterate(devnag_text.decode('utf-8'),'hi',lang_code)
            
            return lang_text
        else:
            return text

if __name__ == '__main__': 

    if len(sys.argv)<4:
        print "Usage: python unicode_transliterate.py <infile> <outfile> <src_language> <tgt_language>"
        sys.exit(1)

    src_language=sys.argv[3]
    tgt_language=sys.argv[4]

    # Do normalization 
    with codecs.open(sys.argv[1],'r','utf-8') as ifile:
        with codecs.open(sys.argv[2],'w','utf-8') as ofile:
            for line in ifile.readlines():
                transliterated_line=UnicodeIndicTransliterator.transliterate(line,src_language,tgt_language)
                ofile.write(transliterated_line)
