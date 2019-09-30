from concurrent.futures import ThreadPoolExecutor, as_completed

class State(object):
    def __init__(self, evaluation, is_candidate):
        """__init__ of State class

        Args:
            evaluation (Number): the evaluation value of a pattern.
            is_candidate (bool): a pattern can be minimal pattern or not.        
        """
        self.evaluation = evaluation
        self.is_candidate = is_candidate
            
        
class MPLIME(object):
    def __init__(self, evaluate):
        """__init__ of MPLIME class

        Args:
            evaluate: a classifier, it returns an evaluation value and a class.
        """
        self.minimal_pattern_family = None
        self.e_init = None
        self.target_class = None
        self.evaluate = evaluate


    def search_minimal_patterns(self, e_init, max_cardinality, mode):
        """function to search minimal patterns

        after executing this function, a found family of minimal patterns is
        set to self.minimal_pattern_family.
        
        Args:
            e_init (List): initial pattern. 
            max_cardinality (int): a parameter to constrain 
                                   the size of self.minimal_pattern_family.
            mode: search mode ("exact", "super", or "disjoint")
        """
        self.minimal_pattern_family = []
        self.e_init = e_init
        eval_init, self.target_class = self.evaluate(e_init)
        checked_patterns = {tuple(e_init): State(eval_init, True)}
        path = []
        # this variable is only used when mode == "exact"
        e_next = e_init.copy()
        
        while len(self.minimal_pattern_family) < max_cardinality:
            e_current = e_next
            e_next, eval_next = None, float("-inf")
            path.append(e_current)

            if len(e_current) > 1:
                with ThreadPoolExecutor() as executor:
                    future_to_pattern = {executor.submit(self.evaluate, e_neighbor): e_neighbor
                                         for e_neighbor in self.__get_neighbors(e_current)
                                         if tuple(e_neighbor) not in checked_patterns.keys()}
                    for future in as_completed(future_to_pattern):
                        e_neighbor = future_to_pattern[future]
                        eval_neighbor, cls = future.result()
                        checked_patterns[tuple(e_neighbor)] = State(eval_neighbor,
                                                                    self.target_class==cls)
                candidates = [(e, checked_patterns[tuple(e)].evaluation)
                              for e in self.__get_neighbors(e_current)
                              if checked_patterns[tuple(e)].is_candidate]
                if candidates != []:
                    e_next, eval_next = max(candidates, key=lambda x: x[1])
            
            if e_next is None:
                self.__update(checked_patterns, e_current, mode, path)
                candidate_keys = list(filter(lambda k: checked_patterns[k].is_candidate,
                                             checked_patterns.keys()))
                if candidate_keys == []:
                    break
                e_next = list(max(candidate_keys, key=lambda k: checked_patterns[k].evaluation))
                path = []


    def __get_neighbors(self, e):
        """it yields neighbor patterns of a given pattern

        Args:
            e: a pattern

        Yields:
            neighbor patterns of e
        """
        length = len(e)
        for i in range(length):
            neighbor = e.copy()
            neighbor.pop(i)
            yield neighbor


    def __update(self, checked_patterns, e, mode, path):
        """it updates self.minimal_pattern_family and check_patterns

        Args:
            checked_patterns: it is itself in self.search_minimal_patterns
            e: a candidate of a minimal pattern
            mode: search mode ("exact", "super", or "disjoint")
            path: a path of patterns. it is used when mode=="exact"
        """
        candidate_keys = filter(lambda k: checked_patterns[k].is_candidate, checked_patterns.keys())
        remove_keys = set()
        if mode == "super":
            self.minimal_pattern_family.append(e)
            # shrink the search space
            for key in candidate_keys:
                e_cand = set(key)
                if e_cand.issuperset(set(e)):
                    remove_keys.add(key)
                    
        elif mode == "disjoint":
            self.minimal_pattern_family.append(e)
            # shrink the search space
            for key in candidate_keys:
                e_cand = set(key)
                if not e_cand.isdisjoint(set(e)):
                    remove_keys.add(key)
            used_features = set(sum(self.minimal_pattern_family, []))
            e_next = sorted(list(set(self.e_init)-used_features), key=self.e_init.index)
            if len(e_next) > 0 and tuple(e_next) not in checked_patterns:
                eval_next, cls = self.evaluate(e_next)
                checked_patterns[tuple(e_next)] = State(eval_next, self.target_class==cls)
                
        elif mode == "exact":
            for e_minimal in self.minimal_pattern_family:
                e_minimal = set(e_minimal)
                if set(e).issuperset(e_minimal):
                    break
            else: # for-else statement
                self.minimal_pattern_family.append(e)
            # shrink the search space
            remove_keys.add(tuple(e))
            remove_keys |= set([tuple(e_parent) for e_parent in path])
            
        for key in remove_keys:
            checked_patterns[key].is_candidate = False


    def show(self, end="\n\n"):
        """it displays minimal patterns in IF-OR-THEN format.
                
        Args:
            end (str): end charactor (optional)
        """
        if len(self.minimal_pattern_family) == 0:
            print("empty rule")
        else:
            print(f"IF   {self.minimal_pattern_family[0]}")
            for e in self.minimal_pattern_family[1:]:
                print(f"OR   {e}")
            print(f"THEN class={self.target_class}", end=end)
