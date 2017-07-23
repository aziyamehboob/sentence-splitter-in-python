import sys
import re
from optparse import OptionParser

DASH = u'\u06D4' # arabic full stop
QUESTION = u'\u061F'
ELLIPSIS = u'\u2026'
BULLET = u'\u2022'
CR = u'\u000D'
SPACE = u'\u0020'
FULL_STOP = u'\u002e'

def split_text(filename, docid, xml):
    text = read_text(filename)
    sentences = find_sentences(text)
    write_output(sentences, filename, xml)

def find_sentences(text):
    text = text.replace('\r','')
    text = text.replace('\n','\n\n')
    reg_bullet = u'\s*%s\s*' % BULLET
    text = re.sub(reg_bullet, '\n\n\n\n\n', text)

    text = text.replace('\t* +\t*$', ' ')

    reg_cr = u'[\n%s][ ]+[\n%s]' % (CR, CR)
    text = re.sub(reg_cr, '\n\n', text)

    reg_space = u'^[\t%s]+$' % SPACE
    text = re.sub(reg_space, '\n\n', text)

    text = text.replace('|','')
    #/(\n{2,}|!|\x{061f}|\x{06D4}|\x{2022}|\x{000d}|\s{2,}|\x{2026}|\x{002e})/
    # '\n{2,}|!|QUESTION|DASH    |BULLET  |CR      |\s{2,}|ELLIPSIS|FULL_STOP'
    regex = u'(\n{2,}|!|%s|%s|%s|%s|\s{2,}|%s|\%s)' % (QUESTION, DASH, BULLET, CR, ELLIPSIS, FULL_STOP)
    p = re.compile(regex)
    sentences = p.split(text)
    return sentences

def write_output(sentences, docid, xml):
    if(xml):
        print ('<DOC docid = "%s" lang = "URD">' % (docid))
    segment_id = 1
    follow_up_punctuation = re.compile('[\n%s%s]' % (CR, BULLET))
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        sent = sent.strip()  # remove whitespace
        if len(sent) < 1:    # skip empty lines
            i = i+2
            continue
        if(xml):
            sys.stdout.write('<SEG id="%s">' % (segment_id))
        sys.stdout.write(sent)
        # check punctuation in following sentence
        # if not newline, CR or BULLET, print it
        next_sent = sentences[i+1]
        if not follow_up_punctuation.match(next_sent):
            sys.stdout.write(next_sent)
        if(xml):
            sys.stdout.write('</SEG>')
        print( '')
        segment_id = segment_id + 1
        i = i + 2
    
def read_text(filename):
    f = None
    if filename == "-":
        f = sys.stdin
    else:
        f = open(filename, "r")
    text = f.read()
    f.close()
    return text
    
if __name__ == "__main__":
    parser = OptionParser(usage="%prog -f file <-d=DOCID> <-x>")
    parser.add_option('-d', '--docid', dest='docid', default=None,
                      help='DocID XXX')
    parser.add_option('-f', '--filename', dest='filename',
                      help='Filename to parse')
    parser.add_option('-x', '--xml',
                      action="store_true", dest='xml', default=False,
                      help='Print text in XML format')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    (options, args) = parser.parse_args()
    split_text(options.filename, options.docid, options.xml)
