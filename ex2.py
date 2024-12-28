
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
        self.harry_inital_loc=harry_loc
        self.generate_variables(initial_observations)#initialize the variabls including the intial and goal variabls

    def get_next_action(self, observations):
         return self.actions[self.counter] #TODO: complete



    def create_variable(self, name,state,direction,vault,dragon,i,j,t):
        """
        יוצר משתנה עם שם ייחודי ותווית זמן.
        """
        full_name = f"{name}, t={t}"
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
            if (i,j) == self.harry_inital_loc:
                self.variables[full_name]=True
        elif state=="dragon":
            if (i,j) == dragon:
                self.variables[full_name]=True
        elif state=="trap":
            self.variables[full_name] = True
        elif state=="vault":
            if (i,j) == vault:
                self.variables[full_name] = True



    def create_action(self, name, t):
        """
        יוצר משתנה פעולה עם שם ייחודי ותווית זמן.
        """
        full_name = f"{name}, t={t}"
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
                for x,y in t:
                    if x=='vault':
                        vault=y
                    elif x=='dragon':
                        dragon=y
                    elif x=='sulfur':
                        flag_Sulfur=True
        for t in range(self.max_steps+1):
            for i in range(self.m):
                for j in range(self.n):
                    # משתני מצב למשבצת
                    for direction in ["up", "down", "left", "right"]:
                        self.create_variable(f"safe(Tile_{i}_{j}, {direction})","safe","direction" ,None,None
                                             ,None,i,j,t)
                    self.create_variable(f"trap(Tile_{i}_{j})","trap",None,vault,dragon,i,j, t)
                    self.create_variable(f"dragon(Tile_{i}_{j})","dragon",None,vault,dragon,i,j, t)
                    self.create_variable(f"vault(Tile_{i}_{j})","vault",None,vault,dragon,i,j, t)
                    self.create_variable(f"harry(Tile_{i}_{j})", "harry",None,vault,dragon,i,j, t)
                    #self.create_variable(f"sulfur(Tile_{i}_{j})", "sulfur", None, vault,dragon,i,j, t)
            self.create_variable(f"collected_hallow", "collected_hallow", None, vault, dragon, 0, 0, t)#intialize goal variable
        t=0 # after initialize all the sulfur variabls to True, if there is no sulfur in harrys current location that implies that we can update the sulfures variabls near the location to False
        if not flag_Sulfur:
             self.trap_Update(t)

    def generate_actions(self):
        """
        מייצר פעולות אפשריות עם משתנים עבור כל שלב זמן.
        """
        for t in range(self.max_steps):
            for i in range(self.m):
                for j in range(self.n):
                    # פעולות תנועה
                    self.create_action(f"move_up(Tile_{i}_{j})", t)
                    self.create_action(f"move_down(Tile_{i}_{j})", t)
                    self.create_action(f"move_left(Tile_{i}_{j})", t)
                    self.create_action(f"move_right(Tile_{i}_{j})", t)
                    # פעולות מיוחדות
                    self.create_action(f"collect_treasure(Tile_{i}_{j})", t)
                    self.create_action(f"destroy_trap(Tile_{i}_{j})", t)

    def trap_Update(self,t):
        x=self.current_place[0]#num row of the current location of harry
        y=self.current_place[1]#num col of the current location of harry
        if 0<=x-1:# the tile from above harry current location
            self.variables[f"trap(Tile_{x-1}_{y}), {t}"] = False
        if x+1<=self.m-1:# the tile  under harry current location
            self.variables[f"trap(Tile_{x + 1}_{y}), {t}"] = False
        if y+1<=self.n-1:# the tile from the right harrys current location
            self.variables[f"trap(Tile_{x}_{y+1}), {t}"] = False
        if 0<=y-1:# the tile from the left harrys current location
            self.variables[f"trap(Tile_{x}_{y - 1}), {t}"] = False

