# -*-coding:Latin-1 -*
# 14/08/2020 14h45
import os  # fonctions propres à l'OS linux, windows,...dont on peut tirer le séparateur système et change dir
import sys
import time
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
import atexit
from tkinter import PhotoImage
import socket
#import fileinput

dir_travail = os.path.abspath(os.path.dirname(__file__))  # find program's directory
print ("startup folder=" + dir_travail)
os.chdir(dir_travail)  # jump to the directory where is "nordvpn countries.py"
long_label_fin = 80

# etat= "" or "non connecté"  means connected or not connected to NordVpn network
etat = "non connecté"
killbit = 0   # état de Killswitch
autoconnbit = 0  # état de autoconnect
CyberSecbit = 0
obfuscatebit = 0
premier_passage = "oui"  # means "first run". If "oui", used to avoid command "nordvpn c country" when country unchanged
clignotement_infini = "oui"
duree_defilement_label_fin = 5
anomalie_internet = 0
pays_initial = ""
city = ""
serveur = ""
index_combo = 1
label_fin_text = " "
label_status = "place"

global pays_affiche
global state
global pays_vpn
global nouv_pays
global server_ip
global max_index_combo
global liste_pays_obfuscate
global max_pays_obfuscate
global liste_tous_pays
global max_tous_pays
global nordvpn_status
global technologie
global les_pays
global lines
technologie=""

# ======================================= check if NordVpn app is installed ====================================
def nordvpn_est_il_installe():      # === NordVpn_is_it_installed()
    global nordvpn_status, label_fin_text
    try:
        subprocess.call("which nordvpn > " + '"' + dir_travail + "/NordVpn_etat.txt" + '"', shell=True)
    except subprocess.CalledProcessError:
        print("02 NordVpn missing on this computer")
    nordvpn_etat = open(dir_travail + "/NordVpn_etat.txt", 'r')
    nordvpn_status = nordvpn_etat.read()
    nordvpn_etat.close()
    os.remove(dir_travail + "/NordVpn_etat.txt")
    # =============le résultat de "which nordvpn" est "/usr/bin/nordvpn" ou rien si nordvpn pas installé
    if "/nordvpn" in nordvpn_status:
        # print("03 NordVpn app found")
        pass
    else:
        print("04 NordVpn app not found on this computer.")
        label_fin_text = "NordVpn was not found on this machine, Check the installation. "
        window.title("NordVpn not found, Check your install. ")
        clignoter_message(label_fin_text, 3)
        sys.exit("NNordVpn not found on this computer..")
# ================================ fin test si nordvpn installé =====================================

# ================ checking internet connection (attention, killswitch prevent connection) ========
def internet_est_il_connecte():
    global  label_fin_text
    if killbit == 1:
        subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    if not internet_ok():
        print('05 Check your connection or type in a terminal the command "nordvpn set killswitch off".')
        label_fin_text = "Check your connection or type in a terminal the command 'nordvpn set killswitch off',\nclose this program, then restart."
        window.title("Check your connection or type in a terminal the command 'nordvpn set killswitch off.")

        while clignotement_infini == "oui":   # passera à non quand sera activé le clic fermer fenêtre
            clignoter_message(label_fin_text)

        if killbit == 1:
            subprocess.call("nordvpn set killswitch on", shell=True)  # rétablit killswitch

        sys.exit("pas d acces à internet")

    if killbit == 1:
        subprocess.call("nordvpn set killswitch on > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

def internet_ok():
    global anomalie_internet
    global killbit
    global dir_travail
    global pays_affiche
    global state
    # == si killbit est à zéro, vérifier quand même killswitch avec "nordvpn set killswitch off"

    subprocess.call("nordvpn set killswitch off > " + '"' + dir_travail + "/Etat_killswitch.txt" + '"', shell=True)
    etat_kill_fich = open(dir_travail + "/Etat_killswitch.txt", 'r')
    reponse_killoff = etat_kill_fich.read()
    etat_kill_fich.close()
    os.remove(dir_travail + "/Etat_killswitch.txt")
    if "Kill Switch is set to 'disabled' successfully." in reponse_killoff:  # killswitch était positionné,faudra le remettre
        killbit = 1
    else:
        killbit = 0
    coups = 0  # we are going to probe many times the internet line

    while coups < 15:
        try:
            socket.create_connection(("www.google.com", 80))  # better to set timeout as well
            state = "internet connecté"
            return True
        except OSError:
            state = "internet non connecté"
            coups = coups + 1
            print('06 vérifiez votre connexion, ou frappez la commande "nordvpn set killswitch off".')
            time.sleep(3)
    anomalie_internet = 1
    return False
# ============================ fin vérif si connecté à internet ===========================================

# =============checks if you logged yourself to nordvpn with the command "nordvpn login --legacy" or if you were already connected there
# ----------------------------------------- and else try to log you in---------------------------------------------------
def ouverture_du_compte():
    global label_fin_text,  login, sortie

    try:
        subprocess.call("nordvpn login --legacy > " + '"' + dir_travail + "/NordVpn_legacy.txt" + '"', shell=True)
    except subprocess.CalledProcessError:
        label_fin_text = "Error !!!! Log you in your NordVPN account (command nordvpn login --legacy)"
        print ("07 Log you in your NordVPN account (command nordvpn login --legacy)")
        login = "non"
    nordvpn_legacy_txt = open(dir_travail + "/NordVpn_legacy.txt", 'r')
    nordvpn_legacy = nordvpn_legacy_txt.read()
    nordvpn_legacy_txt.close()
    os.remove(dir_travail + "/NordVpn_legacy.txt")
    if "You are already logged in" in nordvpn_legacy:
        #print("08 OK, the Nordvpn account is already open")
        bouton_ferme_compte.configure(state=tk.NORMAL)
        login = "oui"
        window.deiconify()
    else:
        #print("09 You must be logged to Nordvpn before launch this program,\nby typing in a terminal the command '"'nordvpn login --legacy'"',")
        #print("10 either here, by  enter now your NordVpn ID and password")

        ouvre_le_compte_nordvpn()

# =============fin vérifie qu'on s'est identifié chez nordvpn avec la commande "nordvpn login --legacy"
# =========================opening the customer account at NordVpn ==============================
def ouvre_le_compte_nordvpn():
    global Nord_ID
    global Nord_Psw, label_fin_text, login
    Nord_ID = tk.StringVar()
    Nord_Psw = tk.StringVar()
    H=150
    L=470
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (L / 2))
    y = int((screen_height / 2) - (H / 2))
    newWindow = tk.Toplevel(window)
    newWindow.title("Identification NordVpn")
    newWindow.geometry('{0}x{1}+{2}+{3}'.format(L, H, x, y))   #centre la fenêtre
    newWindow.configure(bg="light blue")
    newWindow.grab_set()

    label_erreur = tk.Label(newWindow, text="enter ID and password", bg='light blue', fg='blue', justify="right")
    label_erreur.place(x=110, y=35, width= 285)

    def proc_ok():
        label_erreur.configure(text="wait...")
        global Nor_dID, label_fin_text, login
        Nord_ID = ID_Nordvpn.get()
        Nord_Psw = PSW_Nordvpn.get()

        if (Nord_ID == "") and (Nord_Psw == ""):
            label_erreur.configure(text="empty username and password")
            return
        else: # un des deux à blanc ?
            if (Nord_ID == ""):
                label_erreur.configure(text="Enter your NordVpn ID")
                return
            else:
                if (Nord_Psw == ""):
                    label_erreur.configure(text="Enter your password")
                    return

        commande="nordvpn login --legacy --username " + Nord_ID + " --password " + Nord_Psw + "  > " + dir_travail + "/NordVpn_legacy.txt"
        label_patience.configure(text="wait")
        label_patience.update()
        try:
            subprocess.call(commande, shell=True)
        #except subprocess.CalledProcessError:
        except :
            label_fin_text = "Error !!!! Open your NordVPN account (command nordvpn login --legacy)"
            print ("11 Error !!!! Open your NordVPN account (command nordvpn login --legacy)")
            login = "non"
        nordvpn_legacy_txt = open(dir_travail + "/NordVpn_legacy.txt", 'r')
        nordvpn_legacy = nordvpn_legacy_txt.read()
        nordvpn_legacy_txt.close()
        os.remove(dir_travail + "/NordVpn_legacy.txt")

        strleg=str(nordvpn_legacy)
        if strleg.find("You can now connect") > -1:
            label_erreur.configure(text="OK, your NordVpn account is now open")
            # print("12 OK, votre compte est maintenant ouvert")
            login="oui"
            newWindow.destroy()
            bouton_ferme_compte.configure(state=tk.NORMAL)
            window.deiconify()
        else:
            if strleg.find("already logged in") > -1:
                label_erreur.configure(text="your NordVpn account was already open")
                print("13 your NordVpn account was already open")
                login="oui"
                newWindow.destroy()
                bouton_ferme_compte.configure(state=tk.NORMAL)
                window.deiconify()

            else:
                if strleg.find("Make sure your credentials are correct") > -1:
                    # print("14 Make sure your credentials are correct")
                    label_erreur.configure(text="Make sure your credentials are correct")
                    login = "non"
                    label_patience.configure(text="")
                    label_patience.update()
                else:
                    label_erreur.configure(text="?????")
                    label_patience.configure(text="")
                    label_patience.update()
                    pass
        label_erreur.update()
    def proc_annule():
        efface_fichiers()
        # close APP and Terminal
        import signal
        os.kill(os.getppid(), signal.SIGTERM)


    def Key_ID(event):   #  if a key on the ID_Nordvpn entry is pressed
        t = event.keysym
        if (t == "Return") or (t=="Down") :
            PSW_Nordvpn.focus()
        pass
    def Key_Psw(event):   # if a key on the PSW_Nordvpn entry is pressed
        t = event.keysym
        if  t == "Up" :
            ID_Nordvpn.focus()
        else:
            if t == "Return" :
                proc_ok()
            pass
        pass

    def voir_ou_non():
        if checkbutton.var.get():
            PSW_Nordvpn.config(show="*")
        else:
            PSW_Nordvpn.config(show="")
    # =============== capture du clic sur la croix de fermeture de la fenêtre de connexion(sinon, fermeture immédiate)===========
    newWindow.protocol("WM_DELETE_WINDOW", proc_annule)  # action à executer avant de fermer la fenêtre
    # =================================== fin capture du clic sur la croix de fermeture de la fenêtre===========
    checkbutton = tk.Checkbutton(newWindow, text="disp", bg="light blue", activebackground="red", onvalue=False, offvalue=True, command=voir_ou_non)
    checkbutton.var = tk.BooleanVar(value=True)
    checkbutton.place(x=410, y=60)
    checkbutton["variable"] = checkbutton.var

    label_ID_Nordvpn = tk.Label(newWindow, text="ID NordVpn ->", bg='light blue', fg='blue')
    label_ID_Nordvpn.place(x=5, y=10)

    ID_Nordvpn = tk.Entry(newWindow, textvariable=Nord_ID, bg='light blue', fg='black', width=35)
    ID_Nordvpn.pack()
    ID_Nordvpn.place(x=120, y=10)
    ID_Nordvpn.bind("<KeyPress>", Key_ID)


    label_PSW_Nordvpn = tk.Label(newWindow, text="Password ->", bg='light blue', fg='blue')
    label_PSW_Nordvpn.place(x=5, y=60)

    PSW_Nordvpn = tk.Entry(newWindow, textvariable=Nord_Psw, bg='light blue', fg='black', width=35)
    PSW_Nordvpn.place(x=120, y=60)
    PSW_Nordvpn.bind("<KeyPress>", Key_Psw)
    PSW_Nordvpn.default_show_val = PSW_Nordvpn.config(show="*")
    PSW_Nordvpn.config(show="*")

    ID_Nordvpn.focus()

    bouton_OK = tk.Button(newWindow, text="OK", command=proc_ok)
    bouton_OK.place(x=120, y=100)
    bouton_OK.config(width=8)

    label_patience = tk.Label(newWindow, text="", bg='light blue', fg='blue')
    label_patience .place(x=225, y=83)

    bouton_annule = tk.Button(newWindow, text="Cancel", command=proc_annule)
    bouton_annule.place(x=315, y=100)
    bouton_annule.config(width=8)


# ===================================== find NordVpn network status ===============================================
def status_load():
    global nouv_pays
    global pays_deja_connecte
    global pays_initial
    global city
    global etat
    global label_fin_text
    global serveur
    global server_ip
    global pays_affiche
    global killbit , autoconnbit, CyberSecbit, obfuscatebit, technologie, nordvpn_status

    #print ("status_load", obfuscatebit)

    subprocess.call("nordvpn status > " + '"' + dir_travail + "/NordVpn_etat.txt" + '"', shell=True)
    subprocess.call("nordvpn settings >> " + dir_travail + "/NordVpn_etat.txt", shell=True)
    nordvpn_etat = open(dir_travail + "/NordVpn_etat.txt", 'r')
    nordvpn_status = nordvpn_etat.read()
    nordvpn_etat.close()
    os.remove(dir_travail + "/NordVpn_etat.txt")
    if "Obfuscate: enabled" in nordvpn_status:
        obfuscatebit = 1
        tick_obfuscate.select()
        tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan")



        combo_ville.set('')
        combo_ville["values"] = ("")
        combo_ville.configure(state='readonly')
        combo_ville.update()




    else:
        obfuscatebit = 0
        tick_obfuscate.deselect()
        tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan")

        combo_ville.configure(state='normal')
        combo_ville.update()


    if "Kill Switch: enabled" in nordvpn_status:
        killbit = 1


    if obfuscatebit == 1:
        try:
            subprocess.call("nordvpn set obfuscate on > /home/bernard/Documents/toto.txt", shell=True)
        except subprocess.CalledProcessError:
             pass

    subprocess.call("nordvpn status > " + '"' + dir_travail + "/NordVpn_etat.txt" + '"', shell=True)
    subprocess.call("nordvpn settings >> " + '"' + dir_travail + "/NordVpn_etat.txt" + '"', shell=True)
    nordvpn_etat = open(dir_travail + "/NordVpn_etat.txt", 'r')
    nordvpn_status = nordvpn_etat.read()
    nordvpn_etat.close()
    os.remove(dir_travail + "/NordVpn_etat.txt")
    if nordvpn_status.find("Status: Disconnected") > -1:
        label_fin_text = "not connected to NordVpn network"
        window.title("not connected to NordVpn network")

        etat = "non connecté"
        icone_rouge()
    else:
        index_serveur = nordvpn_status.find("Current server:") + 16
        index_fin_serveur = (nordvpn_status.find("Country:")-1)
        serveur = nordvpn_status[index_serveur: index_fin_serveur]

        index_country = index_fin_serveur + 10  # index_country --> 9 caractères après la fin du serveur
        index_fin_country = nordvpn_status.find("City:") - 1
        pays_deja_connecte = nordvpn_status[index_country: index_fin_country]
        pays_initial = pays_deja_connecte.lower()
        pays_initial_corrige=pays_initial.replace(" ","_")
        pays_deja_connecte = pays_initial_corrige
        index_city = index_fin_country + 7  # index_city --> deux caractères avant le mot "City"
        index_fin_city = nordvpn_status.find("Server IP:") - 1
        city = nordvpn_status[index_city: index_fin_city]

        index_server_ip = index_fin_city + 11
        index_fin_server_ip = nordvpn_status.find("Current technology:") - 1
        server_ip = nordvpn_status[index_server_ip: index_fin_server_ip]

        window.title( city + " (serveur=" + serveur + " , IP=" + server_ip + ")")


        label_fin_text = "You are connected to " + city + " ,  " + pays_deja_connecte + " \n(serveur " + serveur + " , IP=" + server_ip + ")  \n "
        clignoter_message("You are connected to " + city + " ,  " + pays_deja_connecte + " \n(serveur " + serveur + " , IP=" + server_ip + ")  \n ")

        icone_verte()
        etat = "connecté"

        if "Technology: NORDLYNX"  in nordvpn_status:
            technologie = 'NordLynx'


            obfuscatebit = 0
            tick_obfuscate.deselect()
            tick_obfuscate.configure(state="disabled")
            tick_obfuscate.update()

        else:
            technologie = 'OpenVpn'

        if "Kill Switch: enabled" in nordvpn_status:
            killbit = 1
            tick_kill.select()
            tick_kill.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            killbit = 0
            tick_kill.deselect()
            tick_kill.configure(bg='light blue', fg='black', activebackground="cyan")

        if "Auto-connect: enabled" in nordvpn_status:
            autoconnbit = 1
            tick_autoconn.select()
            tick_autoconn.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            autoconnbit = 0
            tick_autoconn.deselect()
            tick_autoconn.configure(bg='light blue', fg='black', activebackground="cyan")

        if "Threat Protection Lite: enabled" in nordvpn_status:
            CyberSecbit = 1
            tick_cybersec.select()
            tick_cybersec.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            CyberSecbit = 0
            tick_cybersec.deselect()
            tick_cybersec.configure(bg='light blue', fg='black', activebackground="cyan")
        if "Obfuscate: enabled" in nordvpn_status:
            obfuscatebit = 1
            tick_obfuscate.select()
            tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            obfuscatebit = 0
            tick_obfuscate.deselect()
            tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan")
        if obfuscatebit == 1:
            label_fin_text = label_fin_text + " serveur brouillé (obfuscated)"
        else:
            label_fin_text = label_fin_text + " serveur non brouillé (not obfuscated)"



# =============================== recharge le status de nordvpn initial après changement ===========
def recharge_status():
    global nouv_pays
    global pays_deja_connecte
    global pays_initial
    global city
    global etat
    global label_fin_text
    global serveur
    global server_ip
    global pays_affiche
    global killbit , autoconnbit, CyberSecbit, obfuscatebit, technologie, nordvpn_status

    subprocess.call("nordvpn status > " + '"' + dir_travail + "/NordVpn_etat.txt" + '"', shell=True)
    subprocess.call("nordvpn settings >> " + '"' + dir_travail + "/NordVpn_etat.txt" + '"', shell=True)
    nordvpn_etat = open(dir_travail + "/NordVpn_etat.txt", 'r')
    nordvpn_status = nordvpn_etat.read()
    nordvpn_etat.close()
    os.remove(dir_travail + "/NordVpn_etat.txt")
    if nordvpn_status.find("Status: Disconnected") > -1:
        label_fin_text = "pas connecté au réseau NordVpn"
        window.title("pas connecté au réseau NordVpn")
        icone_rouge()
        etat = "non connecté"

    else:
        index_serveur = nordvpn_status.find("Current server:") + 16
        index_fin_serveur = (nordvpn_status.find("Country:")-1)
        serveur = nordvpn_status[index_serveur: index_fin_serveur]

        index_country = index_fin_serveur + 10  # index_country --> 9 caractères après la fin du serveur
        index_fin_country = nordvpn_status.find("City:") - 1
        pays_deja_connecte = nordvpn_status[index_country: index_fin_country]
        pays_initial = pays_deja_connecte.lower()
        pays_initial_corrige=pays_initial.replace(" ","_")
        pays_deja_connecte = pays_initial_corrige
        index_city = index_fin_country + 7  # index_city --> deux caractères avant le mot "City"
        index_fin_city = nordvpn_status.find("Server IP:") - 1
        city = nordvpn_status[index_city: index_fin_city]

        index_server_ip = index_fin_city + 11
        index_fin_server_ip = nordvpn_status.find("Current technology:") - 1
        server_ip = nordvpn_status[index_server_ip: index_fin_server_ip]

        window.title( city + " (serveur=" + serveur + " , IP=" + server_ip + ")")

        icone_verte()

        label_fin_text = "you exit nordvpn at " + city + " ,  " + pays_deja_connecte + " \n(server " + serveur + " , IP=" + server_ip + ")  \n "
        clignoter_message("you exit nordvpn at " + city + " ,  " + pays_deja_connecte + " \n(server " + serveur + " , IP=" + server_ip + ")  \n ")


        etat = "connecté"

        if "Technology: NORDLYNX"  in nordvpn_status:
            technologie = 'NordLynx'
        else:
            technologie = 'OpenVpn'

        if "Kill Switch: enabled" in nordvpn_status:
            killbit = 1
            tick_kill.select()
            tick_kill.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            killbit = 0
            tick_kill.deselect()
            tick_kill.configure(bg='light blue', fg='black', activebackground="cyan")

        if "Auto-connect: enabled" in nordvpn_status:
            autoconnbit = 1
            tick_autoconn.select()
            tick_autoconn.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            autoconnbit = 0
            tick_autoconn.deselect()
            tick_autoconn.configure(bg='light blue', fg='black', activebackground="cyan")

        if "Threat Protection Lite: enabled" in nordvpn_status:
            CyberSecbit = 1
            tick_cybersec.select()
            tick_cybersec.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            CyberSecbit = 0
            tick_cybersec.deselect()
            tick_cybersec.configure(bg='light blue', fg='black', activebackground="cyan")

        if "Obfuscate: enabled" in nordvpn_status:
            obfuscatebit = 1
            tick_obfuscate.select()
            tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan")
        else:
            obfuscatebit = 0
            tick_obfuscate.deselect()
            tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan")

        if obfuscatebit == 1:
            label_fin_text = label_fin_text + " obfuscated server"
        else:
            label_fin_text = label_fin_text + " not obfuscated server"
# ===================================================================================================================================================




# ================================================init_listes_pays  attention, il y a deux listes (normale et obfuscate) ===============================
def init_listes_pays():
    global obfuscatebit
    global liste_pays_obfuscate, max_pays_obfuscate
    global liste_tous_pays, max_tous_pays
    global index_combo
    global nordvpn_status
    global max_index_combo
    global technologie
    global lines
    global les_pays

    # Arriving here, the "obfuscate" parameter is already set to "on" or "off".The list of countries depending on this parameter, we have to
    # change its value to establish the two lists corresponding to "on" and "off", and then we give back its initial value to "obfuscate".
    # ------- The "NordLynx" technology is not compatible with the "nordvpn set obfuscate on" command. First choose the "openvpn" technology.
    bascule = 0
    if technologie == "NordLynx":
        bascule=1
        subprocess.call("nordvpn set technology OpenVpn > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        truc1 = open(dir_travail + "/Nordvpn_resultat_commande.txt", 'r')
        truc1.close()
        if os.path.exists(dir_travail + "/Nordvpn_resultat_commande.txt"):  # supprime le fichier résidu éventuel
            os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    # -------------------------------------- établit la liste des pays pour serveurs obfuscat=on--------------------------


    if obfuscatebit == 1:       # obfiscate is already set "on", so we can directly load the obfuscated servers list

        commande = "nordvpn countries > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        subprocess.call(commande, shell=True)
        fich = dir_travail + "/Nordvpn_resultat_commande.txt"
        file = open(fich, "r")
        lines = file.read()

        extract_liste_pays(fich)

        obs = []
        l = len(les_pays)
        liste_pays_obfuscate = les_pays
        max_pays_obfuscate = len(liste_pays_obfuscate)

        # ======= ET MAINTENANT, ÉTABLIR LISTE TOUS PAYS

        subprocess.call("nordvpn set obfuscate off >" + dir_travail+ "/Nordvpn_resultat_commande.txt", shell=True)  # passage à settings obfuscate off
        commande="nordvpn countries > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        subprocess.call(commande, shell=True)

        fich = dir_travail + "/Nordvpn_resultat_commande.txt"
        file = open(fich, "r")
        lines = file.read()

        extract_liste_pays(fich)

        obs = []
        l=len(les_pays)
        liste_tous_pays = les_pays
        liste_tous_pays.insert(0, ">>>P2P")
        max_tous_pays=len(liste_tous_pays)
        obfuscatebit = 1        # retour à l'état initial
        tick_obfuscate.select()
        subprocess.call("nordvpn set obfuscate on", shell=True)  # ====retour état initial

    else:   # ================== Obfuscatbit=0, l'état de obfuscate est off
        commande="nordvpn countries > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        subprocess.call(commande, shell=True)

        fich = dir_travail + "/Nordvpn_resultat_commande.txt"
        file = open(fich, "r")
        lines = file.read()     # lecture en un coup de toutes les lignes du fichier
        file.close()

        extract_liste_pays(fich)

        liste_tous_pays = les_pays

        liste_tous_pays.insert(0, ">>>P2P")
        max_tous_pays=len(liste_tous_pays)

        # ======= ET MAINTENANT, ÉTABLIR PAYS obfuscate ON, il faudra revenir à l'état initial Off à la fin
        subprocess.call("nordvpn set obfuscate on > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)  # passer à settings obfuscate on
        commande = "nordvpn countries > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        subprocess.call(commande, shell=True)

        fich = dir_travail + "/Nordvpn_resultat_commande.txt"
        file = open(fich, "r")
        lines = file.read()
        file.close()

        extract_liste_pays(fich)
        liste_pays_obfuscate = les_pays
        max_pays_obfuscate=len(liste_pays_obfuscate)

        subprocess.call("nordvpn set obfuscate off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)  # retour à settings obfuscate off
        obfuscatebit = 0   # retour à l'état initial
        tick_obfuscate.deselect()

    # return to nordlynx if it was the initial technology
    if bascule == 1:
        commande="nordvpn set technology nordlynx > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        subprocess.call(commande, shell=True)
        technologie = "NordLynx"
        bouton_technologie.configure(text="NordLynx")

# ===============================================end of init_listes_pays=======================================


def extract_liste_pays(fich):
    global lines
    global les_pays

    troc=""
    les_pays_str=""
    truc=[]
    modele = "abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ "

    file = open(fich, "r")
    machin=file.readline()
    i=1
    zot=""
    while machin :
        if not "nordvpn.com" in machin:  # ligne de nouveauté de nordvpn
            if machin != "":
                zut=""
                for i in range(0, len(machin)):
                    if machin[i:i + 1] in modele:
                        zut = zut + machin[i:i + 1]
                    else:
                        zut = zut + " "
                # on a remplacé tous les caractères non compris dans modele par blanc
                # et maintenant, on supprime les blancs en trop dans zut
                zot=""
                del_blanc="non"
                b=0
                for i in range (0,len (zut)):
                    if zut[i:i+1] != " " :
                        zot=zot + zut[i:i+1]
                        del_blanc = "non"
                    else :      # caractère blanc
                        if del_blanc == "non" :         # on n'est pas dans une séquence de blancs mais sur le premier blanc de la séquence
                            zot=zot + " "               # on reconduit le blanc
                            del_blanc = "oui"           # et on initialise la suppression des blancs suivants
                        else:                           # on est dans une séquence de suppression de blancs, on ne le reconduit pas
                            b=0
                zot=zot.lower()
        troc = troc + zot
        machin = file.readline()
        i=i+1

    les_pays=troc.split()
    les_pays.sort()


# ====attention ! si obfuscate alors la liste pays est différente.
def select_liste_pays():
    global pays_affiche
    global index_combo
    global dir_travail
    global max_index_combo
    global pays_deja_connecte
    global liste_tous_pays
    global obfuscatebit
    global etat, table_pays
    global liste_pays_obfuscate, max_pays_obfuscate
    global liste_tous_pays, max_tous_pays

    if killbit == 1:  # désactive  killswitch
        subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    if obfuscatebit == 1:
        combo_pays.configure(values=liste_pays_obfuscate)
        max_index_combo = len(liste_pays_obfuscate)
        index_combo=0
        table_pays=liste_pays_obfuscate
    else:
        combo_pays.configure(values=liste_tous_pays)
        max_index_combo = len(liste_tous_pays)
        index_combo = 1
        table_pays=liste_tous_pays
    combo_pays.update()

    if etat == "connecté" :
        i = 0
        while i < max_index_combo:
            combo_pays.current(i)
            truc = combo_pays.get()
            if truc == pays_deja_connecte:
                index_combo = i
                combo_pays.current(i)
                combo_pays.update()
                bouton_pays_choisi.configure(text=truc)
                break
            i = i + 1

        if i >= max_index_combo:  # si pays pas trouvé
            index_combo = 1
            combo_pays.current(1)
            combo_pays.update()
            bouton_pays_choisi.configure(text=combo_pays.get())
            message = label_fin.cget("text")

            icone_rouge()

            clignoter_message("Attention !!! le pays " + pays_deja_connecte + " n'a pas de serveur brouillé, choisissez un pays marqué (*)", 5)
            label_fin.configure(text=message)
            label_fin.update()

    else:
        index_combo = 0
        if obfuscatebit == 0:
            combo_pays.current(1)
        else:
            combo_pays.current(0)
        bouton_pays_choisi.configure(text=combo_pays.get())
        bouton_pays_choisi.update()

    if killbit == 1:  # rétablit l(activité de killswitch
        subprocess.call("nordvpn set killswitch on > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")


    ajoute_les_villes(combo_pays.get())

# ====================================fin select_liste_pays======================================

# ================== si autre pays sélecté, met seulement à jour la fenêtre et le fichier index_combo.txt
def change_choix_pays():
    global index_combo
    global pays_affiche

    bouton_pays_choisi.configure(text=combo_pays.get())
    pays=combo_pays.get()
    print("21 change to ---> " + pays + " ?")
    bouton_pays_choisi.configure(bg="cyan")
    index_combo = combo_pays.current()

    ajoute_les_villes(pays)

# ====================================== fin change_choix_pays ========================================


def ajoute_les_villes(pays):
    global lines
    global les_pays
    global obfuscatebit

    if obfuscatebit == 1:
        les_pays=""
        combo_ville.configure(background="light blue", foreground="light blue", state = "readonly")
        combo_ville.set("")
        combo_ville.update()
        combo_ville.pack_forget()
        label_ville.configure(foreground="gray")
        label_ville.update()
    else:
        fich = dir_travail + "/Nordvpn_resultat_commande_cities.txt"
        commande = "nordvpn cities " + pays + " > " + fich
        subprocess.call(commande, shell=True)
        extract_liste_pays(fich)
        les_pays.insert(0, "any")
        obs = les_pays
        liste_villes = obs
        combo_ville.configure(background="white", foreground="black", state="normal")
        combo_ville["values"] = (liste_villes)
        combo_ville.current(0)
        label_ville.configure(text="City->", bg='light blue', fg='blue')   # = tk.Label(window, text="Ville->", bg='light blue', fg='black')
        label_ville.update()
        combo_ville.update()
        if os.path.exists(dir_travail + "/Nordvpn_resultat_commande_cities.txt"):
            os.remove(dir_travail + "/Nordvpn_resultat_commande_cities.txt")

        bouton_pays_choisi.configure(bg="cyan")
        bouton_pays_choisi.update
# ===================================== un_pays_selecte fonction appelée si événement ComboboxSelected de combo_pays.bind
def un_pays_selecte(eventobject):
    change_choix_pays()        # ========= action effectuée suite à cet événement
# ================================= fin =================================================================================

# ==================================== changement de pays connecté ======================================
def bouton_pays_choisi_action():
    global pays_vpn
    global label_fin_text
    global etat
    global pays_deja_connecte
    global premier_passage
    global bouton_pays_choisi
    global message_P2P, dir_travail
    global obfuscatebit

    message_P2P=""
    bouton_pays_choisi.configure(text=combo_pays.get())
    nouv_pays = combo_pays.get()
    nouv_ville = combo_ville.get()
    ville_vpn=str(nouv_ville)
    if etat == "connecté":
        if pays_deja_connecte == nouv_pays:
            if premier_passage == "oui":
                message = "You are already in " + pays_deja_connecte
                window.title("You exit the VPN in" + nouv_pays)
                icone_verte()
                clignoter_message(message)
                premier_passage = "non"
            else:
                message = "change of server " + nouv_pays
                window.title("You will exit the VPN at " + nouv_pays)

                icone_verte()

                clignoter_message(message)


    if nouv_pays != "":
        pays_vpn = nouv_pays.lower()
    else:
        pays_vpn = pays_deja_connecte.lower()
    if pays_vpn == ">>>p2p":
        # attention, P2P uniquement si technologie OpenVpn.
        if technologie == "NordLynx" :
            print ("22 P2P incompatible with NordLynx technology. Switch to OpenVpn.")
            clignoter_message("P2P incompatible with NordLynx technology. Switch to OpenVpn.")
        else:
            message_P2P=""
            commande="nordvpn c P2P"
            try:
                subprocess.call(commande, shell=True)
            except subprocess.CalledProcessError:
                label_fin_text = "Error, could not connect to P2P"
                print ("23 Error, could not connect to P2P")
            message_P2P="\nserveur P2P"
            # clignoter_message(label_fin_text)
    else:
        # AVANT DE RECONNECTER À UN SERVEUR, ON DÉCONNECTE CELUI EN COURS
        subprocess.call("nordvpn d", shell=True)
        time.sleep(3)
        if obfuscatebit == 1 :
            commande = "nordvpn c " + pays_vpn + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        else:
            if ville_vpn=="any" :
                commande = "nordvpn c " + pays_vpn + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
            else:
                commande = "nordvpn c " + pays_vpn + " " + ville_vpn + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        # print ("commande2=" + commande)

        attente("voir")
        try:
            subprocess.call(commande, shell=True)
        except subprocess.CalledProcessError:
            label_fin_text = "could not connect to " + pays_vpn + " " + ville_vpn
            window.title("could not connect to " + pays_vpn + " " + ville_vpn)
            print ("24 could not connect to " + pays_vpn+  " " + ville_vpn)
            return

        attente("pas voir")
        truc1 = open(dir_travail + "/Nordvpn_resultat_commande.txt", 'r')
        truc2 = truc1.read()

        truc1.close()
        if os.path.exists(dir_travail + "/Nordvpn_resultat_commande.txt"):  # supprime le fichier résidu éventuel
            os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
        if truc2.find("Whoops") > -1:
            print("25 Whoops --------------------------------- houlala")
            return

    subprocess.call("nordvpn status", shell=True)
    bouton_sort_du_vpn["state"] = tk.NORMAL
    bouton_technologie.configure(bg='cyan', fg='black', activebackground="cyan", highlightbackground="cyan")
    recharge_status()

    clignoter_message(label_fin_text + message_P2P)

# ============================================ fin change pays =======================================

# ========================================= actions du bouton technologie
def bouton_technologie_survole(eventobject):
    bouton_technologie.configure(text="click pour changer")
def bouton_technologie_quitte(eventobject):
    if technologie == "OpenVpn" :
        bouton_technologie.configure(text="OpenVpn")
    else:
        bouton_technologie.configure(text="NordLynx")

def bouton_technologie_change(eventobject):
    global obfuscatebit

    if technologie == "NordLynx":
        bouton_technologie.configure(text="NordLynx")
    else:
        bouton_technologie.configure(text="OpenVpn")

# ========================================= fin actions du bouton technologie



# ==================bascule de OpenVpn à nordlynx et inversement quand bouton techno pressé ========

def change_techno():
    global technologie
    global serveur, server_ip, city
    global etat
    global pays_deja_connecte
    global index_combo
    global label_fin_text, obfuscatebit

    clignoter_message(" ")
    if technologie == "OpenVpn":        # on devrait passer à NordLynx, à condition que nob obfuscate qui est incompatible
        if obfuscatebit != 1 :  #alors on peut le faire mais obfuscat interdit
            tick_obfuscate.configure(state="disabled")
            tick_obfuscate.update()
            bouton_technologie.configure(text="NordLynx")
            bouton_technologie.update()
            technologie="NordLynx"
            return
        else:   # alors on doit refuser
            message = "you can't use NordLynx technology if obfuscate is 'on'."
            print("53" + message)
            clignoter_message(message, 3)
            return

    else:       # on est en technologie NordLynx et on devrait passer à openvpn
        obfuscatebit = 0
        tick_obfuscate.deselect()
        tick_obfuscate.configure(state="normal")
        tick_obfuscate.update()
        bouton_technologie.configure(text="OpenVpn")
        bouton_technologie.update()
        technologie="OpenVpn"
        print ("openvpn")
        return


    # =====================================fin change techno ================================================

#  ================================== sélecte ou déselecte killswitch checkbutton=============================

def tick_killswitch():
    global killbit

    if killbit == 0:
        tick_kill.select()
        tick_kill.configure(bg='light gray', fg='black', activebackground="cyan", activeforeground="black")
        killbit = 1
        subprocess.call("nordvpn set killswitch on", shell=True)
    else:
        tick_kill.deselect()
        tick_kill.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")
        killbit = 0
        subprocess.call("nordvpn set killswitch off", shell=True)

# ================================== fin tick_killswitch =============================

#  ================================== sélecte ou déselecte autoconnect checkbutton=============================
def tick_autoconnect():
    global autoconnbit
    global killbit
    if killbit == 1:    # attention !!! si killswitch positionné, la commande nordvpn à passer ne passe pas
        subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    if autoconnbit == 0:
        tick_autoconn.select()
        autoconnbit = 1
        tick_autoconn.configure(bg='light gray', fg='black', activebackground="cyan", activeforeground="black")
        subprocess.call("nordvpn set autoconnect on", shell=True)
    else:
        tick_autoconn.deselect()
        autoconnbit = 0
        tick_autoconn.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")
        subprocess.call("nordvpn set autoconnect off", shell=True)
    if killbit == 1:   # rétablit l(activité de killswitch
        subprocess.call("nordvpn set killswitch on > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

# ============================= fin de sélecte ou déselecte autoconnect checkbutton=============================

# ================================== sélecte ou déselecte cybersec checkbutton=============================
def tick_cybersec():
    global CyberSecbit
    global killbit

    if killbit == 1:    # attention !!! si killswitch positionné, la commande nordvpn à passer ne passe pas
        subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
    if CyberSecbit == 0:
        tick_cybersec.select()
        CyberSecbit = 1
        tick_cybersec.configure(bg='light gray', fg='black', activebackground="cyan", activeforeground="black")
        subprocess.call("nordvpn set cybersec on", shell=True)
    else:
        tick_cybersec.deselect()
        CyberSecbit = 0
        tick_cybersec.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")
        subprocess.call("nordvpn set cybersec off", shell=True)
    if killbit == 1:   # rétablit l(activité de killswitch
        subprocess.call("nordvpn set killswitch on > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

# ============================================= fin tick_cybersec ===========================================

# ============================================ tick_obfuscate_action =========================================
def tick_obfuscate_action():
    global CyberSecbit
    global killbit
    global obfuscatebit
    global pays_deja_connecte, index_combo, etat, liste_tous_pays, combo_pays, bouton_pays_choisi, label_fin_text, technologie, premier_passage, ville_vpn
    global server_ip

    icone_verte()

    if obfuscatebit == 0:       # on est dans le cas non obfuscate et on désire passer à obfuscate
        if technologie=="NordLynx":
            print ("34 obfuscate not compatible with NordLynx. switch from NordLynx to OpenVpn first")
            tick_obfuscate.deselect()
            obfuscatebit = 0
            message = label_fin.cget("text")
            message1 = "Canot obfuscate with nordlynx technology"
            label_fin.configure(text=message1)
            label_fin.update()
            clignoter_message(message1, 4)
            clignoter_message(message)
            tick_obfuscate.configure(state="normal")
            return

    # on est maintenant dans le cas obfuscate ou non, avec technologie OpenVpn et on désire passer à non obfuscate
    if killbit == 1:    # attention !!! si killswitch positionné, la commande nordvpn à passer ne passe pas
            subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
            os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    # rien ne s'oppose plus au passage à obfuscate = on ou off
    if obfuscatebit == 1:   # on est encore obfuscate, on change

        subprocess.call("nordvpn set obfuscate off",shell=True)
        obfuscatebit = 0
    else:
        subprocess.call("nordvpn set obfuscate on", shell=True)
        obfuscatebit = 1

    status_load()       # et on actualise les indicateurs

    message=""
    clignoter_message(message)
    tick_obfuscate.configure(state="disabled")

    if obfuscatebit == 1 :      # on était non obfuscate, et on va être obfuscate à la fin. On prépare obfuscate
        label_ville.configure(text="", bg='light blue', fg='light blue')   # = tk.Label(window, text="Ville->", bg='light blue', fg='black')
        #label_ville.place(x=300, y=85)
        combo_ville.set('')
        #combo_ville.configure(value=[' '])
        combo_ville["values"] = ("")
        combo_ville.configure(state='readonly')
        combo_ville.update()
    else :      # on était obfuscate et on prépare non obfuscate
        obfuscatebit = 0
        combo_ville.configure(state='normal')
        combo_ville.update()
        label_ville.configure(text="City->", bg='light blue', fg='blue') #= tk.Label(window, text="Ville->", bg='light blue', fg='black')
        #label_ville.place(x=300, y=85)
        tick_obfuscate.deselect()


    label_ville.update()


    bouton_pays_choisi.update()

    sauve_pays = combo_pays.get()
    if etat != "connecté":
        message = label_fin.cget("text")
        clignoter_message("")
        clignoter_message(message)

    if killbit == 1:    # attention !!! si killswitch positionné, la commande nordvpn à passer ne passe pas
            subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
            os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    if obfuscatebit == 1:
        tick_obfuscate.configure(bg='light gray', fg='black', activebackground="cyan", activeforeground="black")
        tick_obfuscate.select()
        tick_obfuscate.update()
        # et on doit actualiser la liste des serveurs

    else:  #  new obfuscate est à off
        tick_obfuscate.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")
        tick_obfuscate.deselect()
        tick_obfuscate.update()

    init_listes_pays()

    if obfuscatebit == 1 :
        combo_pays.configure(values=liste_pays_obfuscate)
        ind_maxi = len(liste_pays_obfuscate)
    else:
        combo_pays.configure(values=liste_tous_pays)
        ind_maxi = len(liste_tous_pays)




    index_combo=0
    combo_pays.current(index_combo)
    i=0
    while i < ind_maxi:
        combo_pays.current(i)
        truc = combo_pays.get()
        if truc == sauve_pays :
            index_combo=i
            combo_pays.current(i)
            break
        i = i + 1


    if i >= ind_maxi:        # si pays non trouvé
        index_combo = 0
        #combo_pays.current(0)
        message=label_fin.cget("text")

        icone_rouge()
        combo_pays.current(0)
        clignoter_message("!!!Attention !!! the country " + sauve_pays + " has no obfuscated server, chose another country",8)
        label_fin.configure(text=message)
        label_fin.update()
        combo_pays.configure(values=liste_pays_obfuscate)
        combo_pays.index(1)
        combo_pays.current(0)
        combo_pays.update()
        bouton_pays_choisi.configure(text=combo_pays.get())
        bouton_pays_choisi.update()
        tick_obfuscate.select()
        etat = "non connecté"
        tick_obfuscate.configure(state="normal")
        return
    else:
        ajoute_les_villes(combo_pays.get())
        combo_ville.configure(state="normal")
        combo_ville.update()
        ville_vpn=combo_ville.get()

    icone_rouge()
    combo_pays.current(index_combo)
    bouton_pays_choisi.configure(text=combo_pays.get())

    if etat != "connecté":      # rien à faire sinon réactiver tick_obfuscate
        tick_obfuscate.configure(state="normal")

        print("Not connected ", combo_pays.get(), combo_ville.get(), obfuscatebit)
        clignoter_message("Not connected . " + str(combo_pays.get()) + "  " + str(combo_ville.get()) + " " + str(obfuscatebit), 5)
        label_fin.configure(text="on n'est pas connecté. ")
        label_fin.update()


    else :

        # il reste à reconnecter, si déjà connecté. Déconnecter puis reconnecter
        # si connecté, déconnecter puis reconnecter après change techno
        subprocess.call("nordvpn d  > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        time.sleep(3)
        print ("ici non connecté")
        #========================================================================================

        if obfuscatebit == 0 :
            if ville_vpn == "any":
                commande = "nordvpn c " + pays_deja_connecte + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
            else:
                commande = "nordvpn c " + pays_deja_connecte + " " + ville_vpn + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        else :
            commande = "nordvpn c " + pays_deja_connecte + " " + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        essai="réussi"
        attente("voir")
        try:
            subprocess.check_call(commande, shell=True)
        except subprocess.CalledProcessError:
            print("41 command " + "nordvpn c " + pays_deja_connecte + " > " + dir_travail + "/Nordvpn_resultat_commande.txt   failed")
            clignoter_message("We couldn't connect..., wait some seconds", 5)
            etat = 'non connecté'
            time.sleep(5)
            clignoter_message("a bit of patience", 5)
            essai="loupé"
        if essai=="loupé":
            try:
                subprocess.check_call(commande, shell=True)
            except subprocess.CalledProcessError:
                print("41-a command " + "nordvpn c " + pays_deja_connecte + " > " + dir_travail + "/Nordvpn_resultat_commande.txt   failed")
                clignoter_message("could not connect, try yourself later", 5)
                etat = 'non connecté'
                essai = "loupé"
                return
        attente("ne pas voir")
        truc1 = open(dir_travail + "/Nordvpn_resultat_commande.txt", 'r')
        truc2 = truc1.read()
        truc1.close()
        if os.path.exists(dir_travail + "/Nordvpn_resultat_commande.txt"):  # supprime le fichier résidu éventuel
            os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
        if truc2.find("Whoops") > -1:
            print("42 Whoops We couldn't connect...")
            clignoter_message("couldn't connect, close the app, then try later", 5)
            etat = 'non connecté'
            return
        else:
            if etat=="connecté" :
                message = "reconnected to " + pays_deja_connecte + ", city: " + city + ", server : " + serveur + ", IP: " + server_ip + "\n" + technologie
            else :
                message = "non reconnected to " + pays_deja_connecte + ", city: " + city + ", server : " + "serveur" + ", IP: " + server_ip + "\n" + technologie
            if obfuscatebit == 1:
                fin_message = ", obfuscated server"
            else:
                fin_message = ", not obfuscated server"
            message = message + fin_message
            print("43" + message)
            icone_verte()
            clignoter_message(message)
            etat = 'connecté'

    if killbit == 1:   # rétablit l(activité de killswitch
        subprocess.call("nordvpn set killswitch on > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")

    if obfuscatebit == 1 :
        tick_obfuscate.select()
        tick_obfuscate.configure(state="normal")
        combo_ville.set('')
        combo_ville["values"] = ("")
        combo_ville.configure(state='readonly')
        combo_ville.update()

    else :
        combo_ville.configure(state="normal")
        ajoute_les_villes(pays_deja_connecte)
        tick_obfuscate.deselect()
        tick_obfuscate.configure(state="normal")

    if etat != "connecté":
        if obfuscatebit == 1:
            commande = "nordvpn c " + str(combo_pays.get()) +  " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
        else :
            ville_vpn = str(combo_ville.get())
            if ville_vpn == "any" :
                commande = "nordvpn c " + str(combo_pays.get()) + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"
            else:
                commande = "nordvpn c " + str(combo_pays.get()) + " " + ville_vpn + " > " + dir_travail + "/Nordvpn_resultat_commande.txt"

        #print("commande 3 =" + commande + "<")
        attente("voir")
        time.sleep(3)
        try:
            subprocess.check_call(commande, shell=True)
        except subprocess.CalledProcessError:
            print("43bis " + commande + "  plantée")
            clignoter_message("could not connect, try yourself later", 5)
            etat = 'non connecté'
            return
        truc1 = open(dir_travail + "/Nordvpn_resultat_commande.txt", 'r')
        truc2 = truc1.read()
        truc1.close()
        if os.path.exists(dir_travail + "/Nordvpn_resultat_commande.txt"):  # supprime le fichier résidu éventuel
            os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
        if truc2.find("Whoops") > -1:
            print("42 Whoops We couldn't connect...")
            clignoter_message("Woops    could not connect, try yourself later", 5)
            etat = 'non connecté'
            return
        else:
            if obfuscatebit == 1:
                message = "reconnected to " + str(combo_pays.get()) + " server: " + serveur + ", IP: " + server_ip + "\n" + technologie
                fin_message = ", obfuscated server"
            else:
                message = "reconnected to " + str(combo_pays.get()) + ", city: " + str(combo_ville.get()) + ", serveur: " + serveur + ", IP: " + server_ip + "\n" + technologie
                fin_message = ", server not obfuscated"
            label_fin_text=message+fin_message
            icone_verte()
    attente("ne pas voir")
# ================================= fin tick_obfuscate_action ==============================================

# ============================= déconnecte nordvpn si était connecté ===================================

def deconnecte_vpn():
    global label_status
    global label_fin_text
    global etat
    global killbit

    icone_rouge()

    subprocess.call("nordvpn d > null", shell=True)
    if os.path.exists(dir_travail + "/Liste_Pays.txt"):
        os.remove(dir_travail + "/Liste_Pays.txt")

    if os.path.exists(dir_travail + "/NordVpn_Countries.txt"):
        os.remove(dir_travail + "/NordVpn_Countries.txt")
    if os.path.exists(dir_travail + "/null"):
        os.remove(dir_travail + "/null")
    if os.path.exists(dir_travail + "/Nordvpn_resultat_commande_cities.txt"):
        os.remove(dir_travail + "/Nordvpn_resultat_commande_cities.txt")

    bouton_technologie.configure(bg='light gray', fg='black')

    if etat == "non connecté":
        window.title("You are not connected via NordVpn.")
        label_fin_text = "You are not connected via NordVpn."
        icone_rouge()

    else:
        label_fin_text = "You are disconnected from the NordVpn network."
        window.title("You are disconnected from the NordVpn network.")
        icone_rouge()



    tick_kill.deselect()
    tick_kill.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")
    killbit = 0
    subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
    os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
    bouton_sort_du_vpn["state"] = tk.DISABLED

    clignoter_message(label_fin_text)
# =================================== fin stop vpn ================================================


# ==========================================ferme window ==========================================
def ferme_fenetre():
    global anomalie_internet
    global clignotement_infini
    clignotement_infini = "non"
    if anomalie_internet == 0:
        bouton_sort_du_vpn["state"] = tk.DISABLED
        bouton_pays_choisi["state"] = tk.DISABLED
        bouton_technologie["state"] = tk.DISABLED
        bouton_ferme_appli["state"] = tk.DISABLED
        bouton_ferme_compte["state"] = tk.DISABLED
        combo_pays["state"] = tk.DISABLED
        bouton_pays_choisi["state"] = tk.DISABLED
        tick_kill["state"] = tk.DISABLED
        tick_autoconn["state"] = tk.DISABLED
        tick_cybersec["state"] = tk.DISABLED
        tick_obfuscate["state"] = tk.DISABLED

    efface_fichiers()
    clignoter_message("this is the end my friend")
    adios(duree_defilement_label_fin)
    kill_tout()

# ======================================== kill tout ====================================================
# ======== récupére l'ID du process père (le terminal) et le tue y compris son fils python nordvpn_Fr.py

def kill_tout ():
    efface_fichiers
    # close APP and Terminal
    import signal
    os.kill(os.getppid(), signal.SIGTERM)
    # close APP only
    try:
        window.destroy()
    except:
        pass
    sys.exit()


# ========================================fin kill tout


# ================ capture du clic en haut à droite de la fenêtre pour lancer la procédure "ferme_fenetre"

# ==================================== efface les fichiers temporaires =====================================
def efface_fichiers():
    if os.path.exists(dir_travail + "/Liste_Pays.txt"):
        os.remove(dir_travail + "/Liste_Pays.txt")
    if os.path.exists(dir_travail + "/NordVpn_Countries.txt"):
        os.remove(dir_travail + "/NordVpn_Countries.txt")
    if os.path.exists(dir_travail + "/nordvpn_settings.txt"):
        os.remove(dir_travail + "/nordvpn_settings.txt")
    if os.path.exists(dir_travail + "/NordVpn_legacy.txt"):
        os.remove(dir_travail + "/NordVpn_legacy.txt")
    if os.path.exists(dir_travail + "/Nordvpn_resultat_commande.txt"):
        os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
    if os.path.exists(dir_travail + "/Nordvpn_etat.txt"):
        os.remove(dir_travail + "/Nordvpn_etat.txt")
    if os.path.exists(dir_travail + "/Nordvpn_resultat_commande_cities.txt"):
        os.remove(dir_travail + "/Nordvpn_resultat_commande_cities.txt")


 # ==================================== fin de efface_fichiers ==============================================

# ==================================== ferme le compte nordvpn ==================================
def log_out():
    bouton_ferme_compte.configure(state=tk.DISABLED)
    subprocess.call("nordvpn set killswitch off > " + dir_travail + "/Nordvpn_resultat_commande.txt", shell=True)
    os.remove(dir_travail + "/Nordvpn_resultat_commande.txt")
    subprocess.call("nordvpn logout", shell=True)
    label_fin_text = "Leave Nordvpn account"
    clignoter_message(label_fin_text, 3)
    efface_fichiers()
    kill_tout()
# ==================================== Leave nordvpn account ==================================

#=====================================action fin du programme si on n'execute pas kill_tout===================
def fin_du_programme():
    efface_fichiers()
    print ("46 End of this software")
#=====================================fin de action fin du programme ==========================================

# ================== action si fermeture normale de la fenêtre par clic croix en haut =================
# =======ne s'execute pas car le programme est fermé par os.kill(os.getppid(), signal.SIGTERM) dans Kill_tout
# =======je préfère kill_tout car
if __name__ == "__main__":
     atexit.register(kill_tout)
# ===============================================================================================================

# ===================================== blink a message =========================================
def clignoter_message(text, coups=0):
    global label_status
    global label_fin_text
    global long_label_fin
    basc = 1
    i = 0
    while i < coups:
        if basc == 1:
            label_fin.configure(text=" ", anchor='center')
            label_fin.update()
            time.sleep(0.2)
            basc = 2
        else:
            label_fin.configure(text=text, anchor='center')
            label_fin.update()
            time.sleep(0.8)
            basc = 1
        i = i + 1
    label_fin.configure(text=text, anchor='center')
    label_fin.update()
    bouton_pays_choisi.configure(bg="light gray")
    bouton_pays_choisi.update()
# ==================================== fin clignoter message =====================================

def icone_verte() :
    global imgv
    label_image = tk.Label(window, image=imgv, width=40)
    label_image.place(x=1, y=1)
    window.iconphoto(False, imgv)

def icone_rouge() :
        global imgr
        label_image = tk.Label(window, image=imgr, width=40)
        label_image.place(x=1, y=1)
        window.iconphoto(False, imgr)

# ==================================== scrolling a message ====================================
def adios(duree):
    global long_label_fin
    debut = time.time()
    secondes = 0
    compteur = 0

    blanc = " " * long_label_fin
    chaine = " See you later, auf wieder sehen, hasta luego, au revoir..."
    chaine_deroul = blanc + chaine + blanc
    pos2 = long_label_fin + 1
    pos1 = pos2 - long_label_fin
    posmax = long_label_fin + len(chaine)
    while secondes <= duree:
        if compteur > 200000:    # vitesse de défilement
            compteur = 0
            label_fin_text = chaine_deroul[pos1: pos2]
            label_fin.configure(text=label_fin_text, anchor='center')
            label_fin.update()
            if pos1 > posmax:
                pos2 = long_label_fin + 1
                pos1 = pos2 - long_label_fin
            else:
                pos1 = pos1+1
                pos2 = pos2+1

        compteur = compteur + 1
        secondes = int(time.time() - debut)
# ================================================ fin adios ===========================================================


# ====================================sets up the buttons and initializes them==============================
window = tk.Tk()
window.configure(bg="light blue")
imgr = PhotoImage(file=dir_travail + "/nordvpn-choix-logo40_r.png")
imgv = PhotoImage(file=dir_travail + "/nordvpn-choix-logo40_v.png")
window.iconphoto(False, imgr)                    # make an icon for the taskbar
window.withdraw()   # on ne montrera la fenêtre que si le compte NordVpn est ouvert

label_image = tk.Label(window, image=imgr, width=40)
label_image.place(x=1, y=1)
window.iconphoto(False, imgr)

lab_choisir_pays = tk.Label(window, text="Chose a country --->", bg='light blue', fg='black')
lab_choisir_pays.place(x=60, y=10)

combo_pays = ttk.Combobox(window, width=25)
combo_pays.place_configure(x=210, y=10)
combo_pays.bind("<<ComboboxSelected>>", un_pays_selecte)  # ==action "un_pays_selecte" quand uévénement ComboboxSelected

labeltechno = tk.Label(window, text="Technology -->", bg='light blue', fg='black')
labeltechno.place(x=470, y=10)

bouton_technologie = tk.Button(window, text="------------", command=change_techno)
bouton_technologie.place(x=620, y=5)
bouton_technologie.config(width=15)
bouton_technologie.bind("<Enter>", bouton_technologie_survole)
bouton_technologie.bind("<Leave>", bouton_technologie_quitte)
bouton_technologie.bind("<Return>", bouton_technologie_change)
bouton_technologie.configure(bg='light gray', fg='black', activebackground="cyan", activeforeground="black", highlightbackground="cyan")

tick_kill = tk.Checkbutton(window, text=" Killswitch ", bg='light blue', activebackground="cyan" ,highlightthickness=0, command=tick_killswitch)
tick_kill.place(x=50, y=46)

tick_autoconn = tk.Checkbutton(window, bg='light blue', text=" Autoconnect ", highlightthickness=0, activebackground="cyan", command=tick_autoconnect)
tick_autoconn.place(x=160, y=46)
tick_autoconn.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")

tick_cybersec = tk.Checkbutton(window, bg='light blue', text=" CyberSec ", highlightthickness=0, command=tick_cybersec)
tick_cybersec.place(x=292, y=46)
tick_cybersec.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")

tick_obfuscate = tk.Checkbutton(window, bg='light blue', text=" obfuscated server", highlightthickness=0, command=tick_obfuscate_action)
#tick_obfuscate.place(x=400, y=46)

tick_obfuscate.place(x=425, y=46)


tick_obfuscate.configure(bg='light blue', fg='black', activebackground="cyan", activeforeground="black")

bouton_pays_choisi = tk.Button(window,  bg='pink', fg='black', width=20, text="????", command=bouton_pays_choisi_action)
#bouton_pays_choisi.place(x=100, y=80)

bouton_pays_choisi.place(x=125, y=80)


label_ouvre_vpn=tk.Label(window, text="Open VPN to --->", bg='light blue', fg='black')
label_ouvre_vpn.place(x=5, y=85)

label_ville=tk.Label(window, text="City->", bg='light blue', fg='black')
#label_ville.place(x=300, y=85)

label_ville.place(x=325, y=85)



label_ville.configure(text="City->",bg='light blue', fg='black')

def une_ville_selectee(eventObject):
    bouton_pays_choisi.configure(background="cyan")

combo_ville = ttk.Combobox(window, width=25)
combo_ville.place_configure(x=385, y=83)
combo_ville.bind("<<ComboboxSelected>>", une_ville_selectee)  # ==action "un_pays_selecte" quand événement ComboboxSelected



bouton_sort_du_vpn = tk.Button(window, text="Leave VPN network", activebackground="cyan", fg="gray", state=tk.NORMAL, command=deconnecte_vpn)
bouton_sort_du_vpn.place(x=620, y=80)
bouton_sort_du_vpn.configure(bg='light gray', fg='black', width=15)

bouton_ferme_appli = tk.Button(window, text=" Close App  ", activebackground='cyan', fg="gray", command=ferme_fenetre)
bouton_ferme_appli.place(x=620, y=43)
bouton_ferme_appli.configure(bg='light gray', fg='black', width=15)

bouton_ferme_compte = tk.Button(window, text="  Close account  ", activebackground='cyan', fg="gray", state="disabled", command=log_out)
bouton_ferme_compte.place(x=620,  y=120)
bouton_ferme_compte.configure(bg='light gray', fg='black', width=15)

label_fin = tk.Label(window, width=long_label_fin, text=label_fin_text, bg='light blue', fg='red', font=('courrier', 10))
label_fin.place(relx=0.5, rely=0.75, anchor='center')

label_attente = tk.Label(window, text="", bg='light blue', fg='light blue')
label_attente.place(relx=0, rely=0, anchor='center')

def attente(voir_ou_non):
    if voir_ou_non == "voir":
        label_attente.configure(text="Wait, this may take a while.", bg='light blue', fg='blue')
        label_attente.place(relx=0.50, rely=0.5, anchor='center')
        label_attente.update()
    else:
        label_attente.configure(text="", bg='light blue', fg='light blue')
        label_attente.place(relx=0, rely=00, anchor='center')
        label_attente.update()

# ==============================fin initialisation des checkbutton========================================

# =============== capture du clic sur la croix de fermeture de la fenêtre (sinon, fermeture immédiate)===========
window.protocol("WM_DELETE_WINDOW",  ferme_fenetre)   # action à executer avant de fermer la fenêtre
# =================================== fin capture du clic sur la croix de fermeture de la fenêtre===========
largeur_window=window.winfo_width()
hauteur_window=window.winfo_height()
largeur_screen=window.winfo_screenwidth()
hauteur_screen=window.winfo_screenheight()

window_x=int((largeur_screen/2) - 390)
window_y=int((hauteur_screen /2) - 130)
window.geometry("{}x{}+{}+{}".format(775, 260, window_x, window_y))

nordvpn_est_il_installe()

internet_est_il_connecte()

ouverture_du_compte()

init_listes_pays()

select_liste_pays()

pays_deja_connecte = ""
if "Status: Disconnected" in nordvpn_status:
    window.title("Not connected to network via NordVPN")
    etat = "non connecté"
    bouton_sort_du_vpn["state"] = tk.DISABLED
else:  # cherche le nom du pays où on est déjà connecté
    bouton_sort_du_vpn["state"] = tk.NORMAL
    recharge_status()
    select_liste_pays()
    etat = "connecté"

if "NORDLYNX" in nordvpn_status:
    technologie = 'NordLynx'
    bouton_technologie.configure(text="NordLynx")
    tick_obfuscate.configure(state="disabled")
    obfuscatebit=0
else:
    technologie = 'OpenVpn'
    bouton_technologie.configure(text="OpenVpn")
    tick_obfuscate.configure(state="normal")

if pays_deja_connecte != "" :
    bouton_pays_choisi.configure(text=pays_deja_connecte)

# =============================== actions restant à faire selon la situation =================================

if (etat == "connecté"):
    recharge_status()
    select_liste_pays()

if etat != "connecté":
    icone_rouge()
    message = "Not connected to network via NordVPN"
    clignoter_message(message)
else:
    if premier_passage == "oui":
        icone_verte()
        message = "VPN exit at " + city + " , " + pays_deja_connecte + " \n(server " + serveur + ", IP=" + server_ip + ")"
        if obfuscatebit == 1:
            message = message + "\nobfuscated server"
        else:
            message = message + "\nserver not obfuscated"
        clignoter_message(message)
        label_fin_text=message
        premier_passage = "non"
    else:
        clignoter_message(label_fin_text)





window.mainloop()
