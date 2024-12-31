
ids = ['319000725','207036211']

class GringottsController:

    def __init__(self, map_shape, harry_loc, initial_observations):

        # Timeout: 60 seconds
        self.counter=0
        self.m=map_shape[0] #num rows
        self.n=map_shape[1] #num columns
        self.max_steps=5+3*(self.m+self.n) #maximum number of rounds
        self.current_place=harry_loc
        self.variables={}
        self.actions={}
        self.harry_initial_loc=harry_loc
        self.generate_variables(initial_observations)#initialize the variabls including the initial and goal variabls

    def create_variable(self, name,state,direction,vault,dragon,i,j):
        """
        יוצר משתנה עם שם ייחודי ותווית זמן.
        """
        full_name = f"{name}"
        self.variables[full_name]=False
        if state=="safe":
            if direction=="up":
                if 0 <= i - 1:
                    self.variables[full_name] = True
            elif direction=="down":
                if i + 1 <= self.m-1:
                    self.variables[full_name] = True
            elif direction=="left":
                if j-1 >= 0:
                    self.variables[full_name] = True
            else:
                if j+1 <= self.n-1:
                    self.variables[full_name] = True
        elif state=="harry":
            if (i,j) == self.harry_initial_loc:
                self.variables[full_name]=True
        elif state=="dragon":
            if (i,j) == dragon:
                self.variables[full_name]=True
        elif state=="trap":
            self.variables[full_name] = True
        elif state=="vault":
            if (i,j) == vault:
                self.variables[full_name] = True
        elif state=="checked_vault":
            self.variables[full_name] = False
        elif state == "visited":
            if (i, j) == self.harry_initial_loc:
                self.variables[full_name] = True



    def create_action(self, name):
        """
        יוצר משתנה פעולה עם שם ייחודי ותווית זמן.
        """
        full_name = f"{name}"
        self.actions[full_name] = False


    def generate_variables(self,initial_observations):
        """
        מייצר את כל המשתנים האפשריים עבור כל אריח בלוח ולכל שלב זמן.
        """
        vault=None
        dragon=None
        flag_Sulfur=False
        if len(initial_observations)>0:
            for t in initial_observations:
                x = t[0]
                if x == 'vault':
                    y = t[1]
                    vault = y
                elif x == 'dragon':
                    y = t[1]
                    dragon = y
                elif x == 'sulfur':
                    flag_Sulfur = True
        #for t in range(self.max_steps+1):
        for i in range(self.m):
            for j in range(self.n):
                # משתני מצב למשבצת
                for direction in ["up", "down", "left", "right"]:
                    self.create_variable(f"safe(Tile_{i}_{j}, {direction})","safe","direction" ,None,None
                                         ,i,j)#לא חורג מגבולות המפה
                self.create_variable(f"trap(Tile_{i}_{j})","trap",None,vault,dragon,i,j)
                self.create_variable(f"dragon(Tile_{i}_{j})","dragon",None,vault,dragon,i,j)
                self.create_variable(f"vault(Tile_{i}_{j})","vault",None,vault,dragon,i,j)
                self.create_variable(f"checked_vault(Tile_{i}_{j})", "checked_vault", None, vault, dragon, i, j)#TODO:check if really necceary
                self.create_variable(f"harry(Tile_{i}_{j})", "harry",None,vault,dragon,i,j)
                self.create_variable(f"visited(Tile_{i}_{j})", "visited", None, vault, dragon, i, j)
                #self.create_variable(f"sulfur(Tile_{i}_{j})", "sulfur", None, vault,dragon,i,j, t)
        #self.create_variable(f"collected_hallow", "collected_hallow", None, vault, dragon, 0, 0)#intialize goal variable
        #t=0 # after initialize all the sulfur variabls to True, if there is no sulfur in harrys current location that implies that we can update the sulfures variabls near the location to False
        if not flag_Sulfur:
             self.trap_Update()

    # def generate_actions(self):
    #     """
    #     מייצר פעולות אפשריות עם משתנים עבור כל שלב זמן.
    #     """
    #     for i in range(self.m):
    #         for j in range(self.n):
    #             # פעולות תנועה
    #             self.create_action(f"move_up(Tile_{i}_{j})")#from tile(i,j)
    #             self.create_action(f"move_down(Tile_{i}_{j})")
    #             self.create_action(f"move_left(Tile_{i}_{j})")
    #             self.create_action(f"move_right(Tile_{i}_{j})")
    #             # פעולות מיוחדות
    #             self.create_action(f"collect(Tile_{i}_{j})")
    #             self.create_action(f"destroy trap(Tile_{i}_{j})")

    def trap_Update(self):
        x=self.current_place[0]#num row of the current location of harry
        y=self.current_place[1]#num col of the current location of harry
        if 0<=x-1:# the tile from above harry current location
            self.variables[f"trap(Tile_{x-1}_{y})"] = False
        if x+1<=self.m-1:# the tile  under harry current location
            self.variables[f"trap(Tile_{x + 1}_{y})"] = False
        if y+1<=self.n-1:# the tile from the right harrys current location
            self.variables[f"trap(Tile_{x}_{y+1})"] = False
        if 0<=y-1:# the tile from the left harrys current location
            self.variables[f"trap(Tile_{x}_{y - 1})"] = False


    def dragon_Update(self,dragon_loc):
        """
        update new dragons discoveres
        dragon_loc is the new location we discovered and delivered to this function
        t is the timestamp of the discovery
        """
        i=dragon_loc[0]
        j=dragon_loc[1]
        self.variables[f"dragon(Tile_{i}_{j})"] = True

    def vault_Update(self,vault_loc):
        """
        update new dragons discoveres
        dragon_loc is the new location we discovered and delivered to this function
        t is the timestamp of the discovery
        """
        i = vault_loc[0]
        j = vault_loc[1]
        self.variables[f"vault(Tile_{i}_{j})"] = True

    def checked_vault_Update(self,vault_loc):
        """
        update that we checked that vault in order to prevent double checks in the same vault
        """
        i = vault_loc[0]
        j = vault_loc[1]
        self.variables[f"visited(Tile_{i}_{j})"] = True
        self.variables[f"checked_vault(Tile_{i}_{j})"] = True


    def harry_Update(self,harry_new_loc):
        harry_old_loc=self.current_place
        x_old=harry_old_loc[0]
        y_old=harry_old_loc[1]
        i=harry_new_loc[0]
        j=harry_new_loc[1]
        self.current_place=harry_new_loc
        self.variables[f"harry(Tile_{x_old}_{y_old})"] = False
        self.variables[f"harry(Tile_{i}_{j})"] = True
        self.variables[f"visited(Tile_{i}_{j})"] = True

    def destroy_trap(self,trap_loc):
        """
        destroy a trap in trap_loc
        """
        i = trap_loc[0]
        j = trap_loc[1]
        self.variables[ f"trap(Tile_{i}_{j})"] = False

    def get_possible_actions(self):
        """
        Returns all possible legal actions from current location with improved safety checks.
        Never returns wait action.
        """
        possible_actions = []
        curr_x, curr_y = self.current_place

        # Check if we can collect from current location
        if self.variables[f"vault(Tile_{curr_x}_{curr_y})"] and not self.variables[f"checked_vault(Tile_{curr_x}_{curr_y})"]:
            possible_actions.append(("collect",))

        # Check possible moves in all directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # right, left, down, up
            new_x, new_y = curr_x + dx, curr_y + dy

            # Check if move is within bounds
            if 0 <= new_x < self.m and 0 <= new_y < self.n:
                # Skip if we know there's a dragon
                if self.variables[f"dragon(Tile_{new_x}_{new_y})"]:
                    continue

                # If there's a trap, only offer destroy action
                if self.variables[f"trap(Tile_{new_x}_{new_y})"]:
                    possible_actions.append(("destroy", (new_x, new_y)))
                else:
                    # Only add move action if we're certain it's safe
                    possible_actions.append(("move", (new_x, new_y)))

        return possible_actions

    def get_direction_to_nearest_unvisited(self, x, y):
        """
        Returns the direction to move towards the nearest unvisited tile
        with improved safety checks
        """
        min_distance = float('inf')
        best_neighbor = None

        # First try to find unvisited tiles
        for i in range(self.m):
            for j in range(self.n):
                # Skip known dangerous locations
                if self.variables[f"dragon(Tile_{i}_{j})"]:
                    continue

                if not self.variables[f"visited(Tile_{i}_{j})"]:
                    distance = abs(x - i) + abs(y - j)  # Manhattan distance
                    if distance < min_distance:
                        min_distance = distance
                        best_neighbor = (i, j)

        if best_neighbor is None:
            # If no unvisited tiles, try to find unchecked vaults
            for i in range(self.m):
                for j in range(self.n):
                    if (self.variables[f"vault(Tile_{i}_{j})"] and
                            not self.variables[f"checked_vault(Tile_{i}_{j})"] and
                            not self.variables[f"dragon(Tile_{i}_{j})"]):
                        distance = abs(x - i) + abs(y - j)
                        if distance < min_distance:
                            min_distance = distance
                            best_neighbor = (i, j)

        if best_neighbor is None:
            return None

        # Find the best immediate move towards the target
        curr_x, curr_y = x, y
        target_x, target_y = best_neighbor

        possible_next_moves = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = curr_x + dx, curr_y + dy
            if 0 <= new_x < self.m and 0 <= new_y < self.n:
                # Only consider moves that don't lead to known dangers
                if not self.variables[f"dragon(Tile_{new_x}_{new_y})"]:
                    new_distance = abs(new_x - target_x) + abs(new_y - target_y)
                    possible_next_moves.append(((new_x, new_y), new_distance))

        if possible_next_moves:
            return min(possible_next_moves, key=lambda x: x[1])[0]
        return None

    def get_next_action(self, observations):
        """
        Decide next action based on current state and observations.
        Never returns wait action.
        """
        # Update knowledge base from observations
        vault = None
        dragon = None
        flag_Sulfur = False
        if observations:
            for obs in observations:
                obs_type = obs[0]
                if obs_type == 'vault':
                    vault = obs[1]
                    self.vault_Update(vault)
                elif obs_type == 'dragon':
                    dragon = obs[1]
                    self.dragon_Update(dragon)
                elif obs_type == 'sulfur':
                    flag_Sulfur = True

        if not flag_Sulfur:
            self.trap_Update()

        # Get current possible actions
        possible_actions = self.get_possible_actions()
        if not possible_actions:
            return ("move", self.current_place)  # Stay in place if no other options

        # Priority 1: Collect if at vault
        if ("collect",) in possible_actions:
            self.checked_vault_Update(self.current_place)
            return ("collect",)

        # Priority 2: Move to adjacent unchecked vault
        if vault and not self.variables[f"checked_vault(Tile_{vault[0]}_{vault[1]})"]:
            for action in possible_actions:
                if action[0] == "move" and action[1] == vault:
                    self.harry_Update(vault)
                    return action
                elif action[0] == "destroy" and action[1] == vault:
                    self.destroy_trap(vault)
                    return action


        # Priority 3: Move towards nearest unvisited tile
        next_target = self.get_direction_to_nearest_unvisited(self.current_place[0], self.current_place[1])
        if next_target:
            for action in possible_actions:
                if action[0] == "move" and action[1] == next_target:
                    self.harry_Update(next_target)
                    return action
                elif action[0] == "destroy" and action[1] == next_target:
                    self.destroy_trap(action[1])
                    return action

        # Priority 4: Destroy any reachable trap
        for action in possible_actions:
            if action[0] == "destroy" :
                self.destroy_trap(action[1])
                return action

        # Priority 5: Move to any safe location
        # Prefer unvisited locations
        unvisited_moves = []
        fallback_moves = []

        for action in possible_actions:
            if action[0] == "move":
                x, y = action[1]
                if not self.variables[f"visited(Tile_{x}_{y})"]:
                    unvisited_moves.append(action)
                else:
                    fallback_moves.append(action)

        if unvisited_moves:
            action = unvisited_moves[0]  # Take first unvisited move
            self.harry_Update(action[1])
            return action

        if fallback_moves:
            action = fallback_moves[0]  # Take first available move
            self.harry_Update(action[1])
            return action


