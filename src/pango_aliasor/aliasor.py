class Aliasor:
    def __init__(self, alias_file=None):
        import json

        if alias_file is None:
            import urllib.request, json

            with urllib.request.urlopen(
                "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/pango_designation/alias_key.json"
            ) as data:
                file = json.load(data)

        else:
            with open(alias_file) as file:
                file = json.load(file)

        self.alias_dict = {}
        for column in file.keys():
            if type(file[column]) is list or file[column] == "":
                self.alias_dict[column] = column
            else:
                self.alias_dict[column] = file[column]

        self.realias_dict = {v: k for k, v in self.alias_dict.items()}

    def compress(self, name, assign=False):
        """
        Returns the compressed lineage name. 
        Set assign to True to automatically define new aliases for otherwise unhandled designations. 
        For example, if you want to compress 'BA.5.2.5.6', and if BA.5.2.5 were not an accepted alias, 
        it would assign BA.5.2.5 to the next available code (in this example, EN) and return EN.6.
        Recombinant lineages (prefixed with 'X') are treated as a separate set of available aliases
        and will always return an alias prefixed with 'X'.
        """
        name_split = name.split(".")
        levels = len(name_split) - 1
        num_indirections = (levels - 1) // 3
        if num_indirections <= 0:
            return name
        alias = ".".join(name_split[0 : (3 * num_indirections + 1)])
        ending = ".".join(name_split[(3 * num_indirections + 1) :])
        if assign and alias not in self.realias_dict:
            #note- this cannot produce lineage aliases prefixed with X, which are handled separately as they represent recombinants.
            self.assign_alias(alias)
        return self.realias_dict[alias] + "." + ending

    def uncompress(self, name):
        """
        Returns the uncompressed lineage name.
        """
        name_split = name.split(".")
        letter = name_split[0]
        try:
            unaliased = self.alias_dict[letter]
        except KeyError:
            return name
        if len(name_split) == 1:
            return name
        if len(name_split) == 2:
            return unaliased + "." + name_split[1]
        else:
            return unaliased + "." + ".".join(name_split[1:])
    
    def parent(self, name):
        """
        Returns parent lineage in aliased format or '' if at top level
        """
        return self.compress(".".join(self.uncompress(name).split(".")[:-1]))
    
    def partial_compress(self, name, up_to: int = 0, accepted_aliases: set = {}):
        """
        aliasor.partial_compress("B.1.1.529.3.1",up_to=1) # 'BA.3.1'
        aliasor.partial_compress("B.1.1.529.3.1.1.2",up_to=1) # 'BA.3.1.1.2'

        aliasor.partial_compress("B.1.1.529.3.1",accepted_aliases=["AY"]) # 'B.1.1.529.3.1'
        aliasor.partial_compress("B.1.617.2",accepted_aliases=["AY"]) # 'AY.2'
        """
        # If accepted_aliases is passed without up_to set, then try out all possible values
        name_split = name.split(".")
        levels = len(name_split) - 1
        indirections = (levels - 1) // 3

        alias = name_split[0]

        if up_to > 0:
            if indirections <= up_to:
                return self.compress(name)
            to_alias = ".".join(name_split[0 : (3 * up_to + 1)])
            alias = self.realias_dict[to_alias]
        
        # Compress at least till up_to, maybe further

        # Check if levels beyond up_to (working backwards) are in accepted_aliases
        if accepted_aliases is not {}:
            for level in range(indirections,up_to,-1):
                to_alias = ".".join(name_split[0 : (3 * level + 1)])
                if to_alias in self.realias_dict.keys():
                    if self.realias_dict[to_alias] in accepted_aliases:
                        alias = self.realias_dict[to_alias]
                        return alias + "." + ".".join(name_split[(3 * level + 1) :])

        if name_split[(3 * up_to + 1) :] == []:
            return alias
        return alias + "." + ".".join(name_split[(3 * up_to + 1) :])
    
    @staticmethod
    def _charToB(char):        
        return ord(char)-65

    @staticmethod
    def _bToChar(n, banned='IOX'):
        l = chr(n+65)
        while l in banned:
            n += 1
            l = chr(n+65)
        return l

    @staticmethod
    def _numberToString(n, b=23, banned='IOX'):
        #convert the number to base 23
        if n == 0:
            return [0]
        digits = []
        while n:
            digits.append(int(n % b))
            n //= b
        #convert the base 23 to an alphabet string
        return "".join([Aliasor._bToChar(d,banned) for d in digits[::-1]])

    @staticmethod
    def _stringToNumber(cstr, b=23):
        #convert the string to a base23 number
        digits = [Aliasor._charToB(c) for c in cstr]
        #add the digits up to make a base10 number
        num = 0
        level = 0
        for d in digits[::-1]:
            num += d * b**level
            level += 1
        return num

    def next_available_alias(self, recombinant=False):
        """
        Returns the next available alias string. 
        Tracks recombinants separately; set recombinant to True to get the next available recombinant alias.
        """
        if recombinant:
            current = [Aliasor._stringToNumber(k[1:]) for k in self.alias_dict.keys() if k[0] == 'X']
            return 'X' + Aliasor._numberToString(max(current) + 1)
        else:
            current = [Aliasor._stringToNumber(k) for k in self.alias_dict.keys() if k[0] != 'X']
            return Aliasor._numberToString(max(current) + 1)

    def assign_alias(self, name, recombinant=False):
        """
        Assigns the input name to the next available alias. 
        Set recombinant to True to assign it to the next recombinant alias.
        """
        nextn = self.next_available_alias(recombinant)
        self.alias_dict[nextn] = name
        self.realias_dict[name] = nextn