import re

class NameParser():
    """Class to parse names into their components like first, middle, last, etc. Loosely 
    based on the Lingua-EN-NameParser Perl module). Inspired by Matt Ericson's people.rb
    http://github.com/mericson/people"""

    def __init__(self):
        self.nc = "A-Za-z0-9\\-\\'"
        self.last_name_p = "((;.+)|(((Mc|Mac|Des|Dell[ae]|Del|De La|De Los|Da|Di|Du|La|Le|Lo|St\.|Den|Von|Van|Von Der|Van De[nr]) )?([%s]+)))" % self.nc
        self.mult_name_p = "((;.+)|(((Mc|Mac|Des|Dell[ae]|Del|De La|De Los|Da|Di|Du|La|Le|Lo|St\.|Den|Von|Van|Von Der|Van De[nr]) )?([%s ]+)))" % self.nc
        self.seen = 0
        self.parsed = 0
        self.opts =   {'strip_mr':True, 
                      'strip_mrs':False, 
                      'case_mode':'proper', 
                      'couples':False}

        self.titles = ['Mr\.? and Mrs\.? ',
                      'Mrs\.? ',
                      'M/s\.? ',
                      'Ms\.? ',
                      'Miss\.? ',
                      'Mme\.? ',
                      'Mr\.? ',
                      'Messrs ',
                      'Mister ',
                      'Mast(\.|er)? ',
                      'Ms?gr\.? ',
                      'Sir ',
                      'Lord ',
                      'Lady ',
                      'Madam(e)? ',
                      'Dame ',

                      # Medical
                      'Dr\.? ',
                      'Doctor ',
                      'Sister ',
                      'Matron ',

                      # Legal
                      'Judge ',
                      'Justice ',

                      # Police
                      'Det\.? ',
                      'Insp\.? ',

                      # Military
                      'Brig(adier)? ',
                      'Capt(\.|ain)? ',
                      'Commander ',
                      'Commodore ',
                      'Cdr\.? ',
                      'Colonel ',
                      'Gen(\.|eral)? ',
                      'Field Marshall ',
                      'Fl\.? Off\.? ',
                      'Flight Officer ',
                      'Flt Lt ',
                      'Flight Lieutenant ',
                      'Pte\. ',
                      'Private ',
                      'Sgt\.? ',
                      'Sargent ',
                      'Air Commander ',
                      'Air Commodore ',
                      'Air Marshall ',
                      'Lieutenant Colonel ',
                      'Lt\.? Col\.? ',
                      'Lt\.? Gen\.? ',
                      'Lt\.? Cdr\.? ',
                      'Lieutenant ',
                      '(Lt|Leut|Lieut)\.? ',
                      'Major General ',
                      'Maj\.? Gen\.?',
                      'Major ',
                      'Maj\.? ',

                      # Religious
                      'Rabbi ',
                      'Brother ',
                      'Father ',
                      'Chaplain ',
                      'Pastor ',
                      'Bishop ',
                      'Mother Superior ',
                      'Mother ',
                      'Most Rever[e|a]nd ',
                      'Very Rever[e|a]nd ',
                      'Mt\.? Revd\.? ',
                      'V\.? Revd?\.? ',
                      'Rever[e|a]nd ',
                      'Revd?\.? ',

                      # Other
                      'Prof(\.|essor)? ',
                      'Ald(\.|erman)? ']

        self.suffixes = ['Jn?r\.?,? Esq\.?',
                      'Sn?r\.?,? Esq\.?',
                      'I{1,3},? Esq\.?',

                      'Jn?r\.?,? M\.?D\.?',
                      'Sn?r\.?,? M\.?D\.?',
                      'I{1,3},? M\.?D\.?',

                      'Sn?r\.?',         # Senior
                      'Jn?r\.?',         # Junior

                      'Esq(\.|uire)?',
                      'Esquire.',
                      'Attorney at Law.',
                      'Attorney-at-Law.',

                      'Ph\.?d\.?',
                      'C\.?P\.?A\.?',

                      'XI{1,3}',            # 11th, 12th, 13th
                      'X',                  # 10th
                      'IV',                 # 4th
                      'VI{1,3}',            # 6th, 7th, 8th
                      'V',                  # 5th
                      'IX',                 # 9th
                      'I{1,3}\.?',          # 1st, 2nd, 3rd
                      'M\.?D\.?',           # M.D.
                      'D.?M\.?D\.?']        # M.D.

    def parse(self, name):
        self.seen += 1
        
        out = {}
        out['original'] = name
        
        cleaned = self.clean(name)
        out['title'] = self.get_title(cleaned)
        out['suffix'] = self.get_suffix(cleaned)
        
        for title in self.titles:
            name = self.clean(re.sub(r'(%s)' % title, '', name))
        for suffix in self.suffixes:
            name = self.clean(re.sub(r'(\,?\s?)(%s)$' % suffix, '', name))
            
        parts = self.get_name_parts(name)
        out['parsed'] = parts[0]
        if out['parsed']:
            self.parsed += 1
            
        out['parse_type'] = parts[1]
        out['first'] = parts[2]
        out['middle'] = parts[3]
        out['last'] = parts[4]
        out['clean'] = name
        return out
        
    def clean(self, s):
        "Remove leading/trailing spaces and illegal characters from 'name'"
        # remove illegal characters
        s = re.sub(r'[0-9\-\'\.\&\/\,]', '', s)
        # remove repeating spaces
        s = re.sub(r'\s+', ' ', s)
        # remove leading and trailing spaces
        s = s.strip(' ')
        return s
        
    def get_title(self, name):
        "Get title for the given 'name'"
        for title in self.titles:
            title = re.match(r'(%s)' % title, name)
            if title:
                title = title.group(0)
                return title.strip()
        
    def get_suffix(self, name):
        "Get ending/suffix for given 'name'"
        for suffix in self.suffixes:
            suffix = re.search(r'(%s)$' % suffix, name)
            if suffix:
                suffix = suffix.group(0)
                return suffix.strip()
        
    def get_name_parts(self, name, no_last_name=None):
        "Break 'name' down into its component parts - First, Middle, Last"
        parsed = False
        patt_num = 0
        
        nc = self.nc
        
        if no_last_name:
            last_name_p = ''
            mult_name_p = ''
        else:
            last_name_p = self.last_name_p
            mult_name_p = self.mult_name_p
        
        patterns = [r'^([A-Za-z])\.? (%s)$' % last_name_p,                              # 1 -- R NAGLE
                    r'^([A-Za-z])\.? ([A-Za-z])\.? (%s)$' % last_name_p,                # 2 -- R M NAGLE
                    r'^([A-Za-z])\.([A-Za-z])\. (%s)$' % last_name_p,                   # 3 -- R.M. NAGLE
                    r'^([A-Za-z])\.? ([A-Za-z])\.? ([A-Za-z])\.? (%s)$' % last_name_p,  # 4 -- R M M NAGLE
                    r'^([A-Za-z])\.? ([%s]+) (%s)$' % (nc, last_name_p),                # 5 -- R MICHAEL NAGLE
                    r'^([%s]+) ([A-Za-z])\.? (%s)$' % (nc, last_name_p),                # 6 -- RYAN M NAGLE
                    r'^([%s]+) ([A-Za-z])\.? ([A-Za-z])\.? (%s)$' % (nc, last_name_p),  # 7 -- RYAN M M NAGLE
                    r'^([%s]+) ([A-Za-z]\.[A-Za-z]\.) (%s)$' % (nc, last_name_p),       # 8 -- RYAN M.M. NAGLE
                    r'^([%s]+) (%s)$' % (nc, last_name_p),                              # 9 -- RYAN NAGLE
                    r'^([%s]+) ([%s]+) (%s)$' % (nc, nc, last_name_p)]                  # 10 -- RYAN MICHAEL NAGLE
                    
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                patt_num = patterns.index(pattern)
                break
                
        if patt_num is 0:
            first  = match.group(1)
            middle = ''
            last   = match.group(2)
            parsed = True
            parse_type = 1
        elif patt_num is 1:
            first  = match.group(1)
            middle = match.group(2)
            last   = match.group(3)
            parsed = True
            parse_type = 2
        elif patt_num is 2:
            first  = match.group(1)
            middle = match.group(2)
            last   = match.group(3)
            parsed = True
            parse_type = 3
        elif patt_num is 3:
            first  = match.group(1)
            middle = match.group(2) + ' ' + match.group(3)
            last   = match.group(4)
            parsed = True
            parse_type = 4
        elif patt_num is 4:
            first  = match.group(1)
            middle = match.group(2)
            last   = match.group(3)
            parsed = True
            parse_type = 5
        elif patt_num is 5:
            first  = match.group(1)
            middle = match.group(2)
            last   = match.group(3)
            parsed = True
            parse_type = 6
        elif patt_num is 6:
            first  = match.group(1)
            middle = match.group(2) + ' ' + match.group(3)
            last   = match.group(4)
            parsed = True
            parse_type = 7
        elif patt_num is 7:
            first  = match.group(1)
            middle = match.group(2)
            last   = match.group(3)
            parsed = True
            parse_type = 8
        elif patt_num is 8:
            first  = match.group(1)
            middle = ''
            last   = match.group(2)
            parsed = True
            parse_type = 9
        elif patt_num is 9:
            first  = match.group(1)
            middle = match.group(2)
            last   = match.group(3)
            parsed = True
            parse_type = 10
        return [parsed, parse_type, first, middle, last]

    def proper(self, name):
        # lowercase everything
        fixed = name.lower()
        # uppercase first letter of each word by checking for word boundaries
        fixed = ' '.join([word.capitalize() for word in fixed.split(' ')])
        if re.search(r'Mac[a-z]{2,}[^a|c|i|o|z|j]', fixed, re.IGNORECASE):
            fixed = re.search(r'([A-Za-z\s]+)(Mac)([a-z]+)', fixed, re.IGNORECASE)
            fixed = fixed.group(1).capitalize() + fixed.group(2).capitalize() + fixed.group(3).capitalize()
        elif re.search(r'Mc', fixed, re.IGNORECASE):    
            fixed = re.search(r'([A-Za-z\s]+)(Mc)([a-z]+)', fixed, re.IGNORECASE)
            fixed = fixed.group(1).capitalize() + fixed.group(2).capitalize() + fixed.group(3).capitalize()
        return fixed
        