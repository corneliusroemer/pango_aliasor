#%%
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
        self.pango_list=[]

    def compress(self, name):
        name_split = name.split(".")
        levels = len(name_split) - 1
        num_indirections = (levels - 1) // 3
        if num_indirections <= 0:
            return name
        alias = ".".join(name_split[0 : (3 * num_indirections + 1)])
        ending = ".".join(name_split[(3 * num_indirections + 1) :])
        return self.realias_dict[alias] + "." + ending

    def uncompress(self, name):
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

    
    """
    Can be useful to know lineage substructure
    """
    def enable_expansion(self):
        import urllib.request
        with urllib.request.urlopen(
            "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/lineage_notes.txt"
        ) as data:
            self.pango_list = []
            for line in (data.read()).decode().split("\n")[1:]:
                if line:
                    self.pango_list.append(self.uncompress(line.split()[0]))
    
    """
    Expand the lineage to include all descendants. Use compressed format
    """
    def expand_compress(self, name, exclude=[]):
        if len(self.pango_list) == 0:
            self.enable_expansion()
        full_prefix=self.uncompress(name)
        result=[] 
        exclude_full = set([j for i in exclude for j in self.expand_uncompress(i)]) if exclude else set([])
        if self.uncompress(name) not in exclude_full:
            result.append(self.compress(name)) #hack to make the parent name come first
            exclude_full.add(self.uncompress(name))
        for k in self.pango_list:
            if k not in exclude_full and k.startswith(full_prefix):
                result.append(self.compress(k))
        return result
    """
    Expand the lineage to include all descendants. Use uncompressed format
    """
    def expand_uncompress(self, name, exclude=[]):
        if len(self.pango_list) == 0:
            self.enable_expansion()
        full_prefix=self.uncompress(name)
        result=[]
        exclude_full = set([j for i in exclude for j in self.expand_uncompress(i)]) if exclude else set([])
        if self.uncompress(name) not in exclude_full:
            result.append(self.uncompress(name)) #hack to make the parent name come first
            exclude_full.add(self.uncompress(name))
        for k in self.pango_list:
            if k not in exclude_full and k.startswith(full_prefix):
                result.append(k)
        return result
    

    """
    Carves up an array of pangolin lineages to non-overlapping sublineages. Useful for stack plots and other allocations to prevent double counting.
    """
    def partition_focus(self,vocs,remove_self=True): 
        #instead of prefixes check for proper subsets of expansions, if they exclude them all
        result={}
        voc_dict = {k:{"exclude":set([]),"query":set(self.expand_compress(k))} for k in vocs}
        for i,k in enumerate(vocs):
            if i+1 < len(vocs):
                kset=voc_dict.get(k).get("query")
                for j in vocs[i+1:]:
                    jset=voc_dict.get(j).get("query")
                    if jset.issubset(kset):
                        voc_dict.get(k).get("exclude").update(jset)
                    if kset.issubset(jset):
                        voc_dict.get(j).get("exclude").update(kset)
        for k,v in voc_dict.items():
            if remove_self:
                v.get("exclude").add(k)
            v.get("query").difference_update(v.get("exclude"))
            result[k]=list(v.get("query"))
        return result
    """
    For the given array, produce a dictionary of who subsumes who.
    """
    def map_dependent(self,vocs):
        #instead of prefixes check for proper subsets of expansions
        #doesn't strictly require pango_list expansion could be done with prefix logic
        result={}
        voc_dict = {k:{"exclude":set([]),"query":set(self.expand_compress(k))} for k in vocs}
        for i,k in enumerate(vocs):
            if i+1 < len(vocs):
                kset=voc_dict.get(k).get("query")
                for j in vocs[i+1:]:
                    jset=voc_dict.get(j).get("query")
                    if jset.issubset(kset):
                        result.setdefault(k,set([])).add(j)
                    elif kset.issubset(jset):
                        result.setdefault(j,set([])).add(k)
                    else:
                        result.setdefault(j,set([]))
        return result
    
    """
    For the given array, produce a dictionary mapping of the alias to the full name.
    """
    def map_alias(self,vocs): 
        #instead of prefixes check for proper subsets of expansions, if they exclude them all
        result={}
        for i in vocs:
            compressed=self.compress(i)
            decompressed=self.uncompress(i)
            result[compressed]=decompressed
        return result

    """
    Order a list of vocs by vertical descent so that parent lineages come before their children
    """
    def vd_ordering(self,vocs):
        voc_set=set(vocs)
        def split_lineage(lineage):
            """Split a lineage into sortable parts"""
            return tuple(int(part) if part.isdigit() else part for part in lineage.split('.'))

        def my_key(item):
            return split_lineage(item[0])

        inv_map = {v: k for k, v in self.map_alias(vocs).items()}
        vd_ordered = sorted(inv_map.items(), key=my_key)
        #express the result in terms of the original vocs either aliased or expanded
        result= [i[0] if i[0] in voc_set else i[1] for i in vd_ordered]
        return result

    """
    Return relationship between two lineages. ancestor, descendant, outgroup
    """
    def relationship(self, subject, predicate):
        vocs=[subject,predicate]
        voc_dict = {k:{"exclude":set([]),"query":set(self.expand_compress(k))} for k in vocs}
        for i,k in enumerate(vocs):
            if i+1 < len(vocs):
                kset=voc_dict.get(k).get("query")
        if subject in voc_dict.get(predicate).get("query"):
            return "descendant"
        elif predicate in voc_dict.get(subject).get("query"):
            return "ancestor"
        else:
            return "outgroup"


# %%
