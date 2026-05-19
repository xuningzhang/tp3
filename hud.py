import json
import tkinter as tk
from tkinter import filedialog
import numpy as np
import object
import linked_list
import personalized_exception as pe

class HUD:
    def __init__(self, path_default = "setting_default.json"):
        #Lecture du fichier de configuration
        with open(path_default, "r") as f:
            self.default_setting = json.load(f)
        self.current_setting = self.default_setting
        #Vérifier si le fichier est bien formé (si les clefs du dictionnaire sont présents.)
        self.file_verification()
        
        #Création des variables avec valeurs
        self.time = self.current_setting["time_step"]
        self.round_history = linked_list.LinkedList()

        #Éléments visuelles
        #Fenêtre et Canvas
        self.root = tk.Tk()
        self.x_middle = int(self.current_setting["canvas_dimension"][0]/2)
        self.x_max = self.current_setting["canvas_dimension"][0]
        self.y_max = self.current_setting["canvas_dimension"][1]
        self.bord_color = "darkgreen"
        self.root.geometry(f"{self.current_setting['canvas_dimension'][0]}x{self.current_setting['canvas_dimension'][0]}")
        self.root.config(bg="gray20")
        self.display = tk.Canvas(self.root, width=self.current_setting['canvas_dimension'][0], height=int(self.current_setting['canvas_dimension'][1]), bg="darkblue")
        
        #Autres variables
        self.motion = False
        self.position = True                #Si la position des balles sont à l'endroit du tir.
        self.force_multiplier = self.current_setting["force_multiplier"]
        self.checkb_var = tk.BooleanVar()   #Bord
        self.checkb_var.set(True)
        self.checkb_var2 = tk.BooleanVar()  #Trous
        self.checkb_var2.set(True)
        self.data_var = tk.StringVar()      #N for replay step up/down
        self.data_var2 = tk.StringVar()     #Friction value
        self.border = [
            self.display.create_rectangle(0, 0, self.x_max, 15, fill=self.bord_color, outline=self.bord_color),
            self.display.create_rectangle(self.x_max-15, 0, self.x_max, self.y_max, fill=self.bord_color, outline=self.bord_color),
            self.display.create_rectangle(0, self.y_max-13, self.x_max, self.y_max+3, fill=self.bord_color, outline=self.bord_color),
            self.display.create_rectangle(0, 0, 15, self.y_max, fill=self.bord_color, outline=self.bord_color)
                        ]
        self.holes = [
            self.display.create_oval(8, 8, 34, 34, fill="black", outline="black"),
            self.display.create_oval(self.x_middle-13, 8, self.x_middle+13, 34, fill="black", outline="black"),
            self.display.create_oval(self.x_max-34, 8, self.x_max-8, 34, fill="black", outline="black"),
            self.display.create_oval(8, self.y_max-32, 34, self.y_max-6, fill="black", outline="black"),
            self.display.create_oval(self.x_middle-13, self.y_max-32, self.x_middle+13, self.y_max-6, fill="black", outline="black"),
            self.display.create_oval(self.x_max-32, self.y_max-32, self.x_max-6, self.y_max-6, fill="black", outline="black")
                        ]
        self.objects = []
        self.objects_show = []
        
        #labels
        self.lab1 = tk.Label(self.root, text="Jeu de Billard🎱", font=("Arial",20), bg="gray20", fg="white")
        self.lab2 = tk.Label(self.root, text="angle", bg="gray20", fg="yellow", font=("Arial", 12))
        self.lab3 = tk.Label(self.root, text="force", bg="gray20", fg="yellow", font=("Arial", 12))
        self.lab4 = tk.Label(self.root, text="Tir : 0/0", bg="gray20", fg="yellow", font=("Arial", 12))
        self.lab5 = tk.Label(self.root, text="Étape : 0/0", bg="gray20", fg="yellow", font=("Arial", 12))
        self.lab6 = tk.Label(self.root, text="N :", bg="gray20", fg="yellow", font=("Arial", 12))
        self.lab7 = tk.Label(self.root, text="Coefficient de frottement :", bg="gray20", fg="yellow", font=("Arial", 12))
        #Entrées
        self.spinbox_angle = tk.Spinbox(self.root, from_=0, to=360, bd=2, command=self.arrow_update)
        self.spinbox_force = tk.Spinbox(self.root, from_=0, to=100, bd=2, command=self.arrow_update, increment=10)
        self.spinbox_n = tk.Spinbox(self.root, from_=1, to=100, bd=2, textvariable=self.data_var)
        self.spinbox_friction = tk.Spinbox(self.root, from_=0, to=1, bd=2, increment=0.1, textvariable=self.data_var2, command=self.friction_update)
        self.button_shot = tk.Button(self.root, text="Tirer", command=self.play, bg="yellow", bd=2)
        self.checkbox = tk.Checkbutton(self.root, text="Bord", bg="gray20", fg="white", variable=self.checkb_var, onvalue=True, offvalue=False, command=self.plan_update, )
        self.checkbox2 = tk.Checkbutton(self.root, text="Trous", bg="gray20", fg="white", variable=self.checkb_var2, onvalue=True, offvalue=False, command=self.plan_update)
        self.button_replay_first = tk.Button(self.root, text="|◀", command=self.replay_first, bg="lightblue", bd=2)
        self.button_replay_up = tk.Button(self.root, text="1 ▶", command=self.replay_step_up, bg="lightblue", bd=2)
        self.button_replay_down = tk.Button(self.root, text="◀ 1", command=self.replay_step_down, bg="lightblue", bd=2)
        self.button_replay_last = tk.Button(self.root, text="▶|", command=self.replay_last, bg="lightblue", bd=2)
        self.button_replay_up_n = tk.Button(self.root, text="◀ N", command=self.replay_step_up_n, bg="lightblue", bd=2)
        self.button_replay_down_n = tk.Button(self.root, text="N ▶", command=self.replay_step_down_n, bg="lightblue", bd=2)
        self.button_round_up = tk.Button(self.root, text="tir prochain", command=self.round_up, bg="lightblue", bd=2)
        self.button_round_down = tk.Button(self.root, text="tir précédent", command=self.round_down, bg="lightblue", bd=2)
        self.button_reset = tk.Button(self.root, text="Réinitialiser", command=self.reset_command, bg="darkred", fg="white", bd=2)
        self.button_configure = tk.Button(self.root, text="Changer de configuration", command=self.configure, fg="white", bg="darkgreen", bd=2)
        #Pointeur de direction
        self.arrow = self.display.create_line(0,0,0,0, fill="white", arrow="last")
        #Chargement des balls et du bord
        self.load_objects()
        self.plan_update()
    
    def file_verification(self):
        #Vérifier si les éléments sont tous présents
        for element in ["canvas_dimension", 
                        "object_radius", 
                        "friction_value", 
                        "min_speed", 
                        "force_multiplier", 
                        "time_step", 
                        "objects", 
                        "restitution"]:
            if not element in self.current_setting.keys():
                raise pe.MissingKey(f"Le clef {element} n'est pas présent dans le fichier de configuration.")


    def load_objects(self):
        #Vérifier si les valeurs sont dans l'intervalle permise.
        if self.current_setting["restitution"] > 1 or self.current_setting["friction_value"] < 0:
            raise pe.RestitutionCoefNotInRange("La valeur du coefficient de restitution doit être entre 0 et 1.")
        if self.current_setting["friction_value"] > 1 or self.current_setting["friction_value"] < 0:
            raise pe.FrictionNotInRange("La valeur du coefficient de friction doit être entre 0 et 1.")
        #Vérifier si la ball principale est présente.
        if self.current_setting["objects"] == {}:
            raise pe.NoMainObject("La ball principale n'est pas présente.")
        #Mettre à jour le coefficient de friction affiché dans l'interface graphique.
        self.data_var2.set(str(self.current_setting["friction_value"]))
        #Création de la ball principale.
        side_thickness = 15
        main_obj_data = self.current_setting["objects"]["main"]
        main_obj = object.Object(
                velocity = np.array(main_obj_data["velocity_start"]),
                position = np.array(main_obj_data["position_start"]),
                radius = self.current_setting["object_radius"],
                resistance = self.current_setting["friction_value"],
                epsilon = self.current_setting["min_speed"],
                name = "main",
                color = main_obj_data["color"],
                pos_min = np.array([side_thickness, side_thickness]),
                pos_max = np.array([value - side_thickness for value in self.current_setting["canvas_dimension"]]),
                restitution_coeff = self.current_setting["restitution"]
        )
        #Création des balls secondaires. Les noms sont donnés par ordre.
        self.objects.append(main_obj)
        for i, element in enumerate(self.current_setting["objects"]["others"].values()):
            obj = object.Object(
                velocity = np.array(element["velocity_start"]),
                position = np.array(element["position_start"]),
                radius = self.current_setting["object_radius"],
                resistance = self.current_setting["friction_value"],
                epsilon = self.current_setting["min_speed"],
                name = i,
                color = element["color"],
                pos_min = np.array([side_thickness, side_thickness]),
                pos_max = np.array([value-side_thickness for value in self.current_setting["canvas_dimension"]]),
                restitution_coeff = self.current_setting["restitution"]
            )
            self.objects.append(obj)
    
    #Méthode pour afficher les trous et les bords.
    def plan_update(self):
        if self.checkb_var.get():
            for element in self.border:
                self.display.itemconfig(element, state="normal")
        else:
            for element in self.border:
                self.display.itemconfig(element, state="hidden")
        if self.checkb_var2.get():
            for element in self.holes:
                self.display.itemconfig(element, state="normal")
        else:
            for element in self.holes:
                self.display.itemconfig(element, state="hidden")
    #Le pointeur
    def arrow_update(self):
        #replacer la balle si celle-ci est mal placé
        if not self.position:
            self.replace()

        #Modification de l'angle et du force du pointeur.
        angle = self.spinbox_angle.get()
        force = self.spinbox_force.get()
        self.display.delete(self.arrow)
        self.arrow = self.display.create_line(self.objects[0].position[0], self.objects[0].position[1], 
                                              self.objects[0].position[0] + (25 + int(force)/5)*np.cos(np.radians(int(angle))), 
                                              self.objects[0].position[1] + (25 + int(force)/5)*np.sin(np.radians(int(angle))), 
                                              fill="white", arrow="last", width=2)


    def replace(self):
        self.position = True
        self.button_shot.config(text="Tirer", bg="yellow", fg="black")
        for obj in self.objects_show:
                self.display.delete(obj)
        del self.objects_show[:]
        for obj in self.objects:
                self.objects_show.append(self.display.create_oval(obj.position[0]-obj.radius, 
                                                                  obj.position[1]-obj.radius, 
                                                                  obj.position[0]+obj.radius, 
                                                                  obj.position[1]+obj.radius, 
                                                                  fill=obj.color, 
                                                                  outline="Black"))
    
    
    def play(self):
        #Si l'animation est en cours, le boutton tirer ne fera rien.
        if self.position and not self.motion :
            #Replacer les balls à aux positions initiales si la balle n'est pas bien placé.

            #Rendre les boutons gris
            self.buttons_active(False)
            self.motion = True

            #Ajouter une autre tire
            self.round_history.append(linked_list.LinkedList())

            #Supression du pointeur
            self.display.delete(self.arrow)

            #modification de la vitesse initiale de la ball principale.
            angle = self.spinbox_angle.get()
            force = self.spinbox_force.get()
            self.objects[0].set_velocity(np.array([self.force_multiplier*int(force)*np.cos(np.radians(int(angle))), 
                                                self.force_multiplier*int(force)*np.sin(np.radians(int(angle)))
                                                ]))
            #commencer l'animation
            self.animation()
        elif not self.position:
            self.arrow_update()
    

    def animation(self):
        #Historique des positions
        history = {}

        #Mouvement
        for i, obj in enumerate(self.objects):
            pos = obj.position
            obj.move(self.time)
            self.display.move(self.objects_show[i], obj.position[0]-pos[0], obj.position[1]-pos[1])
            history[obj.name] = obj.position
        self.round_history.get().append(history)

        #Collision
        for i in range(len(self.objects) - 1):
            for j in range(i+1, len(self.objects)):
                self.objects[i].collision(self.objects[j])

        #Calcul du mouvement total de l'ensemble des balls
        total_velocity = 0
        for obj in self.objects:
            total_velocity += np.linalg.norm(obj.velocity)

        #Arrêter l'animation si aucune ball est en mouvement.
        if total_velocity > 0:
            self.root.after(self.time, self.animation)
        else:
            self.arrow_update()
            self.replay_label_update()
            self.motion = False
            self.button_shot.config(bg="yellow")
            self.buttons_active(True)


    def buttons_active(self, status):
        #Modifier la couleur des bouttons pour montrer s'il est possible de le cliquer.
        if status:
            self.button_configure.config(bg="darkgreen")
            self.button_replay_down.config(bg="lightblue")
            self.button_replay_down_n.config(bg="lightblue")
            self.button_replay_first.config(bg="lightblue")
            self.button_replay_last.config(bg="lightblue")
            self.button_replay_up.config(bg="lightblue")
            self.button_replay_up_n.config(bg="lightblue")
            self.button_reset.config(bg="darkred")
            self.button_round_down.config(bg="lightblue")
            self.button_round_up.config(bg="lightblue")
            self.button_shot.config(bg="yellow")
        else:
            self.button_configure.config(bg="grey")
            self.button_replay_down.config(bg="grey")
            self.button_replay_down_n.config(bg="grey")
            self.button_replay_first.config(bg="grey")
            self.button_replay_last.config(bg="grey")
            self.button_replay_up.config(bg="grey")
            self.button_replay_up_n.config(bg="grey")
            self.button_reset.config(bg="grey")
            self.button_round_down.config(bg="grey")
            self.button_round_up.config(bg="grey")
            self.button_shot.config(bg="grey")


    def replay_label_update(self):
        #Mettre à jour les indicateurs du tir et de l'étape pour l'historique des tirs.
        self.lab4.config(text=f"Tir : {self.round_history.index+1}/{self.round_history.len()}")
        self.lab5.config(text=f"Étape : {self.round_history.get().index+1}/{self.round_history.get().size}")


    def replay(self):
        #Mettre les balles aux endroits donnés pendant la recherche dans l'historique.
        if not self.motion:
            #Changer le boutton tirer en remise en position si nécessaire
            if self.position:
                self.button_shot.config(text="Position du Tir", bg="darkblue", fg="white")
                self.position = False
            #Supression des balls présentes et du pointeur
            self.display.delete(self.arrow)
            for obj in self.objects_show:
                self.display.delete(obj)
            del self.objects_show[:]
            #Replacer les balls aux endroits
            history = self.round_history.get().get()
            for obj in self.objects:
                self.objects_show.append(self.display.create_oval(history[obj.name][0]-obj.radius, 
                                                                  history[obj.name][1]-obj.radius, 
                                                                  history[obj.name][0]+obj.radius, 
                                                                  history[obj.name][1]+obj.radius, 
                                                                  fill=obj.color, 
                                                                  outline="Black"))
            #Mettre à jour la position dans l'historique
            self.replay_label_update()


    def friction_update(self):
        #Modification du friction à partir de l'interface graphique
        #La friction peut seulement être modifier si les balles ne sont pas en mouvement
        if not self.motion:
            base_friction = self.current_setting["friction_value"]
            value = float(self.data_var2.get())
            if value < 0 or value > 1:
                tk.messagebox.showerror("Erreur", f"La valeur du fiction doit être entre 0 et 1")
                self.data_var2.set(f"{base_friction}")
            else:
                for obj in self.objects:
                    obj.resistance = value
        else:
            tk.messagebox.showerror("Erreur", f"La valeur du friction ne peut pas être changer pendant l'animation.")
            self.data_var2.set(str(self.objects[0].resistance))

    def replay_first(self):
        #Boutton |◀
        if self.round_history.size != 0 and not self.motion:
            self.round_history.get().set_cursor(0)
            self.replay()


    def replay_step_up(self):
        #Boutton 1 ▶
        if self.round_history.size != 0 and not self.motion:
            self.round_history.get().step_up()
            self.replay()


    def replay_step_down(self):
        #Boutton ◀ 1
        if self.round_history.size != 0 and not self.motion:
            self.round_history.get().step_down()    
            self.replay()


    def replay_last(self):
        #Boutton ▶|
        if self.round_history.size != 0 and not self.motion:
            self.round_history.get().set_cursor(self.round_history.get().size - 1)
            self.replay()


    def replay_step_up_n(self):
        #Boutton ▶ n
        if self.round_history.size != 0 and not self.motion:
            increment = int(self.data_var.get())
            if self.round_history.get().index - increment >= 0:
                self.round_history.get().set_cursor(self.round_history.get().index - increment)
                self.replay()
            else:
                self.replay_first()


    def replay_step_down_n(self):
        #Boutton n ◀
        if self.round_history.size != 0 and not self.motion:
            increment = int(self.data_var.get())
            if self.round_history.get().index + increment < self.round_history.get().size:
                self.round_history.get().set_cursor(self.round_history.get().index + increment)
                self.replay()
            else:
                self.replay_last()


    def round_up(self):
        #Boutton prochain tir
        if self.round_history.size != 0 and not self.motion:
            self.round_history.step_up()
            self.replay()


    def round_down(self):
        #Boutton tir précédent
        if self.round_history.size != 0 and not self.motion:
            self.round_history.step_down()
            self.replay()
    

    def reset_command(self):
        #Boutton réinitialisation
        try:
            self.reset()
        except pe.InMotion as e:
            tk.messagebox.showerror("Erreur", e)


    def reset(self, setting = None, resize = False):
        #Changement de configuration selon un configuration donné
        #Si une configuration est donné, la configuration actuelle est celle qui est donnée
        if setting is not None:
            self.current_setting = setting
        
        #Vérifier si la configuration est correcte.
        self.file_verification()

        #La changement de configuration ne peut pas être faite quand les balles sont en mouvement.
        if self.motion:
            raise pe.InMotion("Impossible de réinitialiser pendant un mouvement")
        
        #Mettre les balles au position original
        for obj in self.objects_show:
            self.display.delete(obj)
        del self.objects_show[:]
        del self.objects[:]
        self.load_objects()
        for obj in self.objects:
            self.objects_show.append(self.display.create_oval(obj.position[0]-obj.radius, obj.position[1]-obj.radius, obj.position[0]+obj.radius, obj.position[1]+obj.radius, fill=obj.color, outline="Black"))
        
        #Supression de l'historique
        self.round_history = linked_list.LinkedList()

        #Mettre à jour l'affichage de l'historique
        self.lab4.config(text="Tir : 0/0")
        self.lab5.config(text="Étape : 0/0")

        #Réinitialisation des autres valeurs.
        self.plan_update()
        self.arrow_update()

        #Réinitialisation de la position des bouttons et des textes si nécessaire
        if resize:
            self.root.geometry(f"{self.current_setting['canvas_dimension'][0]}x{self.current_setting['canvas_dimension'][0]}")
            self.display.config(width=self.current_setting['canvas_dimension'][0], height=int(self.current_setting['canvas_dimension'][1]))
            self.show()


    def configure(self):
        #Lecture d'une autre configuration
        path = filedialog.askopenfilename()

        #Le changement de configuration est annulé si aucun fichier n'a été donné
        if path != "":
            try:
                current_dimension = self.current_setting["canvas_dimension"]
                with open(path, "r", encoding='utf-8') as fichier:
                    self.current_setting = json.load(fichier)
                self.reset(resize=current_dimension != self.current_setting["canvas_dimension"])

            #Gestion des exceptions
            except pe.InMotion as e:
                tk.messagebox.showerror("Erreur",e)

            except pe.FrictionNotInRange as e:
                tk.messagebox.showerror("Erreur du fichier de configuration",f"{e}\nVeuillez vérifier si la valeur du coefficient de friction\ncorrespond à l'intervalle permise.\nVeuillez vérifier si votre fichier de configuration est correctement formé.\nLes configrations seront réinitialisées aux valeurs par défaut.")
                self.reset(setting=self.default_setting, resize=True)
            
            except pe.RestitutionCoefNotInRange as e:
                tk.messagebox.showerror("Erreur du fichier de configuration",f"{e}\nVeuillez vérifier si la valeur du coefficient de restitutin\ncorrespond à l'intervalle permise.\nVeuillez vérifier si votre fichier de configuration est correctement formé.\nLes configrations seront réinitialisées aux valeurs par défaut.")
                self.reset(setting=self.default_setting, resize=True)
            
            except pe.NoMainObject as e:
                tk.messagebox.showerror("Erreur du fichier de configuration",f"{e}\nLe fichier de configuration doit contenir au moins la ball principale.\nVeuillez vérifier si votre fichier de configuration est correctement formé.\nLes configrations seront réinitialisées aux valeurs par défaut.")
                self.reset(setting=self.default_setting, resize=True)

            except pe.MissingKey as e:
                tk.messagebox.showerror("Erreur du fichier de configuration",f"{e}\nVeuillez vérifier si votre fichier de configuration est correctement formé.\nLes configrations seront réinitialisées aux valeurs par défaut.")
                self.reset(setting=self.default_setting, resize=True)

            except Exception as e:
                tk.messagebox.showerror("Erreur", f"{e}\nLes configrations seront réinitialisées aux valeurs par défaut.")
                self.reset(setting=self.default_setting, resize=True)


    def show(self):
        #Placement des positions des bouttons
        x_middle = int(self.current_setting["canvas_dimension"][0]/2)
        y_canvas = self.current_setting["canvas_dimension"][1]

        self.lab1.pack()
        #Canvas
        self.display.pack(anchor="w")
        #Angle
        self.spinbox_angle.place(x=60, y=y_canvas+50, height=30, width=80)
        self.lab2.place(x=10, y=y_canvas+55, height=20, width=50)
        #Force
        self.spinbox_force.place(x=x_middle-40, y=y_canvas+50, height=30, width=80)
        self.lab3.place(x=x_middle-90, y=y_canvas+55, height=20, width=50)
        #Play
        self.button_shot.place(x=x_middle+55, y=y_canvas+49, height=34, width=x_middle-60)
        #Setting
        self.checkbox.place(x=10, y=y_canvas+90, height=30, width=80)
        self.checkbox2.place(x=90, y=y_canvas+90, height=30, width=80)
        #Replay
        self.lab4.place(x=110, y=y_canvas+125, height=30, width=60)
        self.button_round_up.place(x=185, y=y_canvas+130, height=23, width=90)
        self.button_round_down.place(x=10, y=y_canvas+130, height=23, width=90)
        #Replay 2
        self.lab5.place(x=40, y=y_canvas+150, height=30, width=200)
        self.button_replay_first.place(x=10, y=y_canvas+180, height=30, width=40)
        self.button_replay_up_n.place(x=55, y=y_canvas+180, height=30, width=40)
        self.button_replay_down.place(x=100, y=y_canvas+180, height=30, width=40)
        self.button_replay_up.place(x=145, y=y_canvas+180, height=30, width=40)
        self.button_replay_down_n.place(x=190, y=y_canvas+180, height=30, width=40)
        self.button_replay_last.place(x=235, y=y_canvas+180, height=30, width=40)
        self.lab6.place(x=280, y=y_canvas+180, height=30, width=30)
        self.spinbox_n.place(x=310, y=y_canvas+180, height=30, width=40)
        #Additional buttons
        self.button_reset.place(x=10, y=y_canvas+220, height=30, width=100)
        self.button_configure.place(x=120, y=y_canvas+220, height=30, width=150)
        #Friction
        self.lab7.place(x=10, y=y_canvas+260, height=30, width=200)
        self.spinbox_friction.place(x=210, y=y_canvas+260, height=30, width=100)
        #Objects show
        for element in self.objects:
            self.objects_show.append(self.display.create_oval(element.position[0]-element.radius, element.position[1]-element.radius, element.position[0]+element.radius, element.position[1]+element.radius, fill=element.color, outline="Black"))
        #arrow show
        self.arrow_update()
    
    def launch(self):
        self.show()
        self.root.mainloop()