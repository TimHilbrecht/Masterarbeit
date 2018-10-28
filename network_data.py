
from gurobipy import *
import network_model
import Winddaten

# Liste für die prozentualen Anteil der installierten Windleistung die zum in Gebiet[g] Periode[y] Saison[s] Tag[t] Zeitpunkt[h] ins Netz einspeist
L_Wind = []

# Liste der halbstündigen Zeitschritte für einen Tag
Zeitschritte = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

# Länge der stündlichen Intervalle h [h]
n_h = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

# Planperiode 
Periode = [1,2]

# Anzahl wie oft Tag t in einer Woche auftritt
n_t = [5,2]

# Anzahl wiederholender Wochen in einer Saison
n_s = [26,26]

# Anzahl von widerholenden Jahre in einer Periode
n_j = [1,1]

# Tagestyp: Wochentag, Wochenende
Tag =["WT","WE"]

# Anzahl Typtag d pro Woche
n_WT = 5
n_WE = 2

# Saison: Sommer, Winter
Saison = ["Winter", "Sommer"]

# Dictionary für Ressourcen
Ressourcen = ["Strom","Wasserstoff"]

Gebiete = ["Aachen","Berlin"]

Technologien = ["WEA", "Elektrolyseur"]

# Trennung der Infrastruktur und der Transporttechnologie, da manche Transporttechnologien diesselebe Infrastruktur teilen
# z.B.:  LKW fürs H2, Benzin und Flüssigerdgas benutzen alle die Infrastruktur "Straße" => Infrastruktur muss nicht für jede Technologie seperat errichtet werden 
Infrastruktur = ["Rohrleitung", "Straße"]

# R_b gibt an ob Verbindung durch Infrastruktur b bidirektional oder unidirektional genutzt werden kann
# R_b = -1: Verbindung ist unidirektional und kann nur in eine Richtung genutzt werden (zb. Leitungen für CO2)
# R_b = 0: Verbindung ist unidirektional aber es können zwei seperate Verbindungen in beide Richtungen errichtet werden (zb. Straße, Schiene)
# R_b = 1: Verbindung ist bidirektional => Nutzung in beide Richtungen möglich (z.b. H2 Rohrleitung, Stromübertragungsleitung)
R_b = [1,0] 

Transport_Tech = ["Fluss", "LKW_H2"] 

# Transportkosten für Nutzung von Transport_Tech l pro km
Transportkosten_l = [0.1,1]

# Transport Umwandlungsfaktor durch Transport_Tech l von Ressource r (Gebiet g ist Senke)
U_Faktor_Transport_dst = [
                    [0,1],
                    [0,1]
                    ]

# Transport Umwandlungsfaktor durch Transport_Tech l von Ressource r (Gebiet g ist Quelle)
U_Faktor_Transport_src = [
                    [0,-1],
                    [0,-1]
                    ]


# LB gibt an ob Transport_Tech l die Infrastruktur b nutzen kann (LB=1) oder nicht (LB=0)
LB = [
      [1,0], # Transport_Tech Fluss kann Infrastruktur Rohrleitung nutzen
      [0,1]  # Transport_Tech LKW kann Infrastruktur Straße nutzen
      ]

# Distanzmatrix zwischen Gebiet g und Gebiet g1 [km]
Distanz = [
        [0,10],
        [10,0]
        ]

# max Kapazität von Infrastruktur b [MW]
b_b_max = [1000, 1000]

# max Übetragungsrate von Transport_Tech l [MW]
q_l_max = [1000, 1000]




# Verb_g_g1 gibt an ob zwischen Gebiet g und g1 eine Transportverbindung aufgebaut werden darf (Verb_g_g1=1) oder nicht (Verb_g_g1=0) 
# Aus Effizenzgründen der Rechnenleistung sind Verbindungen nur für geographisch angrenzende Gebiete erlaubt
Verb_g_g1 = [
            [0,1],
            [1,0]
            ]

# max Produktionsrate von Technologie p [MW] 
P_Tech_max = [4.2,70]

Speicher = ["Wasserstoffspeicher"]

# Umwandlungsfaktor von Ressource r durch Technologie t
W_Tech = [
        [0,-1], # Umwandlungsfaktor von Ressource Strom für Technologie p
        [0,0.6] # Umwandlungsfaktor von Ressource Wasserstoff für Technologie p
        ] 

# Umwandlungsfaktor für Laden von Ressource r in Speicher a (Gebiet ist Quelle des Flusses)
U_Faktor_put_src = [
                    [0],     # kein Stromspeicher
                    [-1]]   # Ladefaktor von Wasserstoff in Wasserstoffspeicher

# Umwandlungsfaktor für Laden von Ressource r in Speicher a (Gebiet ist Senke des Flusses)
U_Faktor_put_dst = [
                    [0],     # kein Stromspeicher
                    [1]]   # Ladefaktor von Wasserstoff in Wasserstoffspeicher

# Umwandlungsfaktor für Halten von Ressource r in Speicher a (Gebiet ist Quelle des Flusses)
U_Faktor_hold_src = [
                    [0],     # kein Stromspeicher
                    [1]]   # Haltefaktor von Wasserstoff in Wasserstoffspeicher

# Umwandlungsfaktor für Halten von Ressource r in Speicher a (Gebiet ist Senke des Flusses)
U_Faktor_hold_dst = [
                    [0],     # kein Stromspeicher
                    [0]]   # Selbstentladenung von Wasserstoff in Wasserstoffspeicher

# Umwandlungsfaktor für Entladen von Ressource r in Speicher a (Gebiet ist Quelle des Flusses)
U_Faktor_get_src = [
                    [0],     # kein Stromspeicher
                    [-1]]   # Entladefaktor von Wasserstoff in Wasserstoffspeicher

# Umwandlungsfaktor für Entladen von Ressource r in Speicher a (Gebiet ist Senke des Flusses)
U_Faktor_get_dst = [
                    [0],     # kein Stromspeicher
                    [1]]   # Ladefaktor von Wasserstoff in Wasserstoffspeicher

# Max Ladeleistung von Speicher s [MW]
S_get_max = [5]

# Max Entladeleistung von Speicher s [MW]
S_put_max = [5]

# Max Speicherkapazität von Speicher s [MWh]
S_hold_max = [30]

# Kosten für neu installierte WEA [€/MW]
K_WEA = 10





D = {}
for r in range(len(Ressourcen)):
    for g in range(len(Gebiete)):
        for j in range(len(Periode)):
            for s in range(len(Saison)):
                for t in range(len(Tag)):
                    for h in range(len(Zeitschritte)):
                        if j==0 and r==1:
                            D[r,g,j,s,t,h] = 20 # Wasserstoffnachfrage Periode 1
                        elif j==1 and r==1: 
                            D[r,g,j,s,t,h] = 50 # Wasserstoffnachfrage Periode 2
                        else:
                            D[r,g,j,s,t,h] = 0

Winddaten.Wind(Gebiete, Periode, Saison, Tag, Zeitschritte, L_Wind)
                    
model = network_model.solve(Gebiete, Saison, Periode, Tag, Zeitschritte, D, L_Wind, K_WEA, Infrastruktur,
                            Transport_Tech, LB, Distanz, b_b_max, q_l_max, Verb_g_g1, R_b, Transportkosten_l,
                            U_Faktor_Transport_dst, U_Faktor_Transport_src,
                            Technologien, W_Tech, Ressourcen, Speicher, P_Tech_max, U_Faktor_put_src,
                            U_Faktor_put_dst, U_Faktor_hold_src, U_Faktor_hold_dst, U_Faktor_get_src,
                            U_Faktor_get_dst, S_get_max, S_hold_max, S_put_max, n_h, n_t, n_s, n_j)                  