# The script of the game goes in this file.
# I hate python.

# Declare characters used by this game. The color argument colorizes the
# name of the character.


define e = Character("Eileen")
init:
    $ _game_menu_screen = None
init python:
    
    import os
    import random

    # DATA CLASSES --------------------------------------

    class Suspect:
        def __init__(self, name, info):
            self.name = name
            self.info = info
            self.status = "Alive"
            self.storedEvidence = []
            self.firstDay = 0

    class Evidence:
        def __init__(self, name, character, depends, header, content, images):
            self.name = name
            self.character = character
            self.depends = depends
            self.header = header
            self.content = content
            self.images = images

    # LOADING FUNCTIONS ---------------------------------

    def GetNameFromPath(path):
        return path[path.rfind("/") + 1 : path.rfind(".")]

    def LoadAllMusic():
        folder = renpy.loader.transfn("radio_songs/")
        files = os.listdir(folder)

        for file in files:
            songs.append("radio_songs/" + file)

    def LoadAllMemos():
        folder = renpy.loader.transfn("resources/Memos/")

        files = os.listdir(folder)

        for file in files:
            LoadMemo(folder + file)

    def LoadMemo(path):
        file = open(path, "r")

        name = GetNameFromPath(path)

        memo = ""

        for line in file:
            memo += line

        file.close()

        memos[name] = memo

    def LoadAllCharacters():
        folder = renpy.loader.transfn("resources/Characters/")

        files = os.listdir(folder)

        for file in files:
            LoadCharacter(folder + file)
            
    def LoadCharacter(path):
        file = open(path, "r")

        name = GetNameFromPath(path)

        info = { }

        for line in file:
            parts = line.strip().split(":")
            info[parts[0]] = parts[1].replace("\\n", "\n\t")

        file.close()

        suspects[name] = Suspect(name, info)
        LoadAllEvidence(name)

    def LoadAllEvidence(character):
        folder = renpy.loader.transfn("resources/Evidence/" + character + "/")

        files = os.listdir(folder)

        for file in files:
            LoadEvidence(folder + file, character)

    def LoadEvidence(path, character):
        file = open(path, "r")

        name = GetNameFromPath(path)

        if name.endswith("_Incomp"):
            name = name[0 : name.rfind("_Incomp")]

        header = ""
        content = ""
        images = []
        depends = []

        mode = 0

        for line in file:
            if line.startswith("header:"):
                mode = 1
            elif line.startswith("content:"):
                mode = 2
            elif line.startswith("images:"):
                mode = 3
            elif line.startswith("depends:"):
                mode = 4
            elif mode == 1:
                header += line
            elif mode == 2:
                content += line
            elif mode == 3:
                images.append(line.strip())
            elif mode == 4:
                depends.append(line.strip())

        file.close()

        evidence[name] = Evidence(name, character, depends, header, content, images)

    lastmemo = ""
    def storeMemo(notes):
        global lastmemo, arrestMemos
        lastmemo = ""
        for note in arrestMemos:
            lastmemo += memos[note] + "\n"
        arrestMemos = []

        for note in notes:
            if type(note) == type(("","","")):
                if type(note[1]) == type([]):
                    ok = True
                    for p in note[1]:
                        ok = ok and suspects[p].status == note[2]
                    if ok:
                        lastmemo += memos[note[0]] + "\n"
                elif suspects[note[1]].status == note[2]:
                    lastmemo += memos[note[0]] + "\n"
            elif type(note) == type(""):
                lastmemo += memos[note] + "\n"

    # INIT CODE ---------------------------

    days = []
    songs = []
    curSongIndex = -1
    suspects = {}
    evidence = {}
    memos = {}
    LoadAllCharacters()
    LoadAllMemos()
    LoadAllMusic()

    notebook = []
    noteToRemove = -1

    numEvidence = 0
    curevidence = []

    govtSuspects = ["Charles O'Brien", "Roland McDowell", "Wendy King"]
    govtArrested = ""

    curday = 1
    numdays = 11

    numEvStored=0
    EvLimit=16 #lowered but IDK if it is lowered enough

    doorClicked = False
    folderClicked = False
    cabinetClicked = False
    notebookClicked = False
    binderClicked = False
    radioClicked= False

    banksFree=False
    eggFree=False

    plantClicks = 0
    plantTapeDay = 0
    glueMessage = False

    allowSkip = False

    def clickPlant():
        global plantClicks, plantTapeDay, glueMessage
        if plantClicks == 0:
            Notify("By the way, don't mess with those plants. They're very expensive!")()
        elif plantClicks == 1:
            Notify("Hey, you might have forgotten, but please don't touch those potted plants!")()
        elif plantClicks == 2:
            Notify("Those plants are there for a reason, you know!")()
        elif plantClicks == 3:
            Notify("Without those plants, this office would look really lifeless!")()
        elif plantClicks == 4:
            Notify("If you keep messing with the potted plants, I'm going to have to bring it up at our next review!")()
        elif plantClicks == 5:
            Notify("Alright, you've left me no choice. We'll see what upper management has to say about this.")()
            plantTapeDay = curday
        elif plantTapeDay == 0 or plantTapeDay == curday:
            Notify("Be careful. You're on thin ice.")()
        elif glueMessage == False:
            Notify("Due to your little plant game, we've had to glue down all the plants. Great job.")()
            glueMessage = True

        plantClicks += 1

    def clickDoor():
        global doorClicked
        if (doorClicked == False):
            doorClicked = True
            Notify("Use the door to leave once you're done reviewing the day's files.")()

        if len(curevidence) > 0 and allowSkip == False:
            Notify("Don't think about leaving until you've read all the evidence!")()
            renpy.play("locked_door.mp3", "sound")
        else:
            renpy.play("Room_Open.mp3", "sound")
            Jump("l_nextDay")()

    def clickFolder():
        global folderClicked
        if (folderClicked == False):
            folderClicked = True
            Notify("Use the folder to read the day's evidence.")()

        if len(curevidence) > 0:
            Jump("l_next_ev")()
        else:
            Notify("No new evidence.")()

    def clickCabinet():
        global cabinetClicked
        if (cabinetClicked == False):
            cabinetClicked = True
            Notify("Use the cabinet to read stored evidence and detain suspicious individuals.")()
        
        Jump("l_files")()

    def clickNotebook():
        global notebookClicked
        if (notebookClicked == False):
            notebookClicked = True
            Notify("Use the notebook to keep track of your reasoning.")()
        
        Jump("l_notebook")()

    def clickBinder():
        global binderClicked
        if (binderClicked == False):
            binderClicked = True
            Notify("Use the binder to re-read the day's memo.")()
        
        Jump("l_binder")()

    arrestReports = []
    arrestMemos = []

    config.log = "debuglog.txt"
    
    nr_banks_arrested = """In response to the all-too-recent burglary of a federal mint, the FBI has arrested a Robert Banks. An investigation of Banks' property revealed, according to the federal agents, that another burglary attempt was in the near future of Banks' plans. The FBI declined to comment on how they came across the information used in making the arrest."""
    
    nr_banks_free = """A federal mint has been robbed again, although this time unsuccessfully. A man identified as Robert Banks was caught in the act of the robbery, and has been arrested by federal officials. Two mint employees were severely injured, but there were no deaths. The government has issued a statement that it will be taking measures to increase security and ensure such an incident will never happen again."""
    
    nr_pearson_arrested = """Locals are left in shock as the affectionately nicknamed "paranoid Pearson" was taken in by federal authorities yesterday. His wife is currently in the hopsital for heart complications and was unavailable for comment, but Pearson's sister-in-law provides us with an image of his personality: "He always insisted on using pay phones and taking overly long routes to prevent 'them' from keeping tabs on him. Maybe his antics only drew their attention, instead of preventing it." The FBI declined to comment on his detainment, or how they came across the information used in making the arrest."""
    
    nr_smith_arrested = """An arrest has been made by federal authorities linking a Julia Smith to a drug lord known by the street name "Butcher". Officials claim that she has been using meat and beef as cover-ups for transportation of her drugs. The FBI declined to comment on her detainment."""
    
    nr_sieland_arrested = """Renowned film director Georg Sieland, who has directed movies such as "Dancing with Daisies" and his most recent work, "Coal", has been arrested by federal agents on charges of Soviet collusion. His recent films have been argued by critics to contain sympathetic views to Communism. Critics and fans alike are split in their beliefs of Sieland's alleged spying. The FBI declined to comment on his detainment."""
    
    nr_webber_free = """A new novel has been taking the literary world by storm! "Danger at the Drama", a mystery thriller by debut author Charlene Webber, tells a gripping tale of danger, deceit, and explosions. "Getting the information about the bombs was the most difficult part," Webber told one journalist. "There was no easy way to find exact information, but I wanted to be as accurate as possible. I'm only surprised no one found me more suspicious!" """
    
    nr_eggleston_arrested = """The federal authorities have arrested a Walter Eggleston on suspicion of criminal intent. He has been described by friends and family as a fun-loving and carefree person. His relations told us they were greatly distressed by his arrest.

"If they're arresting our innocent son without any hard evidence, how are any of us supposed to sleep at night?" his mother said.

The federal authorities have declined to reveal the information they used to determine his intent, or where they came across such information."""

    nr_eggleston_free = """Everyone is left in states of grief and shock as the Department of Motor Vehicles was attacked. Shots were fired from within the building, leaving dozens dead and many more hospitalized. As one of the survivors said when asked for comment, "it's frightening, and I only wish that there had been some way to know that this was happening, and that it could have been prevented." The criminal responsible was identified to be Walter Eggleston, a man described as fun-loving and carefree. He has been taken in by local authorities and is being held without bail."""

    nr_flossi_arrested = """Margot Flossi, the woman who won the lottery only a scant few days ago, is now under arrest by federal authorities. They revealed that they have reason to believe she was planning crimes against the country, but offered no further comments on how they came by this information."""

    nr_flossi_free = """A 70-year-old woman has won the 3.5 million dollar lottery! Margot Flossi purchased the ticket at her local Price-Deal Supermarket. "I've been using the same number for years," Flossi told us in an interview. "I knew they would win someday!" Flossi also mentioned that she plans to take an extended vacation with one of her friends."""

    nr_green_arrested = """A professional golfer has been arrested on charges of suspicious activity and Soviet collusion. Candace Green recently played in the Golf Putter National tournament, placing second to last. Friends of the golfer claimed that lately she seemed absent-minded and less focused on her golfing career, but declined to tell them why.

The federal authorities have declined to comment on where they obtained their information for the arrest."""

    nr_ianson_arrested = """A local college student, Terrence Ianson, has been arrested on charges of suspicious intent by the federal authorities. Friends and family expressed shock and outrage at his arrest.

"He's been nothing but a hard worker and a bundle of fun," Claudia Ianson, Ianson's sister, fumed to our journalists. "I don't understand what 'proof' there is against him!"

The federal authorities have declined to comment on where they came across their incriminating evidence, or even what this evidence is. Protests are expected to be held at Ianson's college regarding his arrest."""

    def removeNoteAt(index):
        notebook.pop(index)
        renpy.jump("l_notebook")

    def clickRadio():
        global radioClicked
        global curSongIndex
        if (radioClicked == False):
            radioClicked = True
            Notify("Use the radio to listen to 80's music.")()

            
        renpy.music.set_volume(0.3, 0.0, channel="music")

        curSongIndex += 1

        if (curSongIndex >= len(songs)):
            curSongIndex = 0

        renpy.play(songs[curSongIndex], "music")

    def arrest(name):
        global arrestReports
        suspects[name].status = "Arrested"

        if curday < 10 or name in ["Charles O'Brien", "Roland McDowell", "Wendy King"]:
            arrestMemos.append(name.split(" ")[1])

        if name == "Robert Banks":
            arrestReports.append((nr_banks_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))
        elif name == "Norman Pearson":
            arrestReports.append((nr_pearson_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))
        elif name == "Julia Smith":
            arrestReports.append((nr_smith_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))
        elif name == "Georg Sieland":
            arrestReports.append((nr_sieland_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))
        elif name == "Walter Eggleston":
            arrestReports.append((nr_eggleston_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))
        elif name == "Margot Flossi":
            arrestReports.append((nr_flossi_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))
        elif name == "Terrence Ianson":
            arrestReports.append((nr_ianson_arrested, "Portaits_Big/" + name.replace(" ", "_") + ".png"))

        renpy.jump("l_files")

    def addEvidence(name):
        for depend in evidence[name].depends:
            if depend != "" and suspects[depend].status != "Alive":
                return
        curevidence.append(name)

    def storeEvidence(name):
        susp = suspects[evidence[name].character]
        if len(susp.storedEvidence) == 0:
            susp.firstDay = curday

        susp.storedEvidence.append(name)
        global numEvStored
        numEvStored+=1

        renpy.jump("l_stored_main")

    def shredStored():
        global numEvStored
        numEvStored-=1

    def showImages(name):
        for img in evidence[name].images:
            ui.image(img)

    def refreshClock():
        num=0
        if numEvidence > 0:
            num = 4 * len(curevidence) / numEvidence
        else:
            num=4
        s = "bg office " + str((4 - num) + 1)
        renpy.log(s)
        renpy.scene()
        renpy.show(s)

    # why python
    def removeAll(name):
        char=suspects[name]
        while len(suspects[name].storedEvidence)>0:
            for ev in char.storedEvidence:
                shredStored()
                suspects[name].storedEvidence.remove(ev)   
        renpy.call("l_files")

    def showStickNote():
        index = (curday / 2) + 1
        if index > 5:
            index = 5
        ui.image("Notes/Note_" + str(index) + ".png", xpos = 100, ypos = 600)

    def showNotebook():
        for num in range(len(notebook)):
            ui.hbox()
            ui.button(action=lambda index=num: removeNoteAt(index)) # kill me pls
            ui.text(notebook[num], style='button_text', color="#000000")
            ui.close()

    def showCharacterFile(name):
        char = suspects[name]
        for ev in char.storedEvidence:
            ui.button(action=lambda f=ev: renpy.call("l_show_ev", f))
            ui.text(ev, style='button_text')

    def showCharacterFiles():
        keys = suspects.keys()
        keys.sort(key = lambda k : suspects[k].firstDay)
        for char in keys:
            if len(suspects[char].storedEvidence) > 0 or suspects[char].status=="Arrested":
                ui.hbox()
                ui.image("Portaits/" + char.replace(" ", "_") + ".png")
                ui.vbox()
                ui.text(char, color="#000000")
                for val in suspects[char].info:
                    ui.text("  " + val + ": " + suspects[char].info[val], color="#000000")
                ui.close()
                ui.vbox()
                if curday > 1:
                    if suspects[char].status == "Alive" and ((not char in govtSuspects) or (govtArrested == "")):
                        ui.button(action=lambda c=char: renpy.call("l_arrest", c))
                        if char in govtSuspects:
                            ui.text("Report!", style='button_text')
                            
                        else:
                            ui.text("Detain!", style='button_text')
                    elif suspects[char].status != "Alive" or (not char in govtSuspects):
                        ui.button()
                        
                        if char in govtSuspects:
                            ui.text("Reported", style='button_text')
                        else:
                            ui.text("Detained", style='button_text')
                ui.button(action=lambda c=char: renpy.call("l_char_file", c))
                ui.text("View Files", style='button_text')
                if curday>1:
                    if len(suspects[char].storedEvidence)>0:
                        ui.button(action=lambda c=char: renpy.call("l_shredAll",c))
                        ui.text("Shred All", style='button_text')
                ui.close()
                ui.close()

screen show_newEvidence(name, isStored):
    image "Cabinet_Base.png" xpos -7 ypos 150    
    if isStored:
        if numEvStored>EvLimit/4*3:
            image "Cabinet_Open_100.png" xpos -7 ypos 150
        elif numEvStored>EvLimit/2:
            image "Cabinet_Open_75.png" xpos -7 ypos 150
        elif numEvStored>EvLimit/4:
            image "Cabinet_Open_50.png" xpos -7 ypos 150
        elif numEvStored>0:
            image "Cabinet_Open_25.png" xpos -7 ypos 150
        else:
            image "Cabinet_Open.png" xpos -7 ypos 150 

    
    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600
    image "Door_Closed.png" xpos 1520 ypos 0  
    image "Notebook_Closed.png" xpos 350 ypos 650 
    image "Binder_Closed.png" xpos 1400 ypos 600
    side "c b r":
        add Solid("#FFFFFF", xsize=650, ysize=850, xpos=-25, ypos=-25)
        area(660, 140, 600, 800)
    
        vbox:
            ysize 800
            text evidence[name].header color "#000000" ypos 35
            hbox:
                ysize 530
                viewport id "vp":
                    ysize 530
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    vbox:
                        xsize 580
                        xalign 0.5 yalign 0.0
                        spacing 10
                        text evidence[name].content color "#000000"
                        $showImages(name)
                
            if isStored:
                if curday>1:
                    textbutton "Shred Evidence" action [(lambda n=name: suspects[evidence[n].character].storedEvidence.remove(n)), (lambda: shredStored()), Call("l_char_file", evidence[name].character)]
                textbutton "Return" action (lambda n=name: renpy.call("l_char_file", evidence[n].character))
            else:
                if curday>1:
                    textbutton "Shred Evidence" action [Play("sound", "Cut_shred.mp3"), Jump("l_main")]
                if numEvStored >= EvLimit:
                    textbutton "Store Evidence" action [Notify("Filing Cabinet full, empty space to store"), (lambda ev=name: addEvidence(ev)), Jump("l_main")]
                else:
                    textbutton "Store Evidence" action [Play("sound", "File_Stored.mp3"), (lambda ev=name: storeEvidence(ev))]
    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"


screen show_notebook():
    image "Door_Closed.png" xpos 1520 ypos 0
    image "Cabinet_Base.png" xpos -7 ypos 150   
    
    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600
    image "Notebook_Open.png" xpos 350 ypos 650
    image "Binder_Closed.png" xpos 1400 ypos 600
    side "c b r":
        add Solid("#FFFFFF", xsize=650, ysize=850, xpos=-25, ypos=-25)
        area(660, 140, 600, 800)
        
        vbox:
            ysize 800
            text "NOTEBOOK\n(Click a note to remove)" color "#000000" ypos -25
            hbox:
                ysize 650
                ypos 0
                viewport id "vp":
                    ysize 650
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    vbox:
                        xsize 580
                        xalign 0.5 yalign 0.0
                        spacing 10
                        $showNotebook()
                        #text notebook color "#000000"
                    
            hbox:
                textbutton "Add Note" action Jump("l_note")
                textbutton "Return" action Jump("l_main")

    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"



screen buttons():
    if len(curevidence) > 0:
        imagebutton:
            xpos 1520 ypos 0
            idle "Door_Closed.png"
            hover "Door_Closed.png"
            action clickDoor
    else:
        imagebutton:
            xpos 1520 ypos 0
            idle "Door_Closed.png"
            hover "Door_Open.png"
            action clickDoor
    
    image "Cabinet_Base.png":
        xpos -7 ypos 150
    
    imagebutton:
        xpos -7 ypos 150
        idle "Cabinet_Closed.png"
        if numEvStored>EvLimit/4*3:
            hover "Cabinet_Open_100.png"
        elif numEvStored>EvLimit/2:
            hover "Cabinet_Open_75.png"
        elif numEvStored>EvLimit/4:
            hover "Cabinet_Open_50.png"
        elif numEvStored>0:
            hover "Cabinet_Open_25.png"
        else:
            hover "Cabinet_Open.png"
        action clickCabinet

    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600

    imagebutton:
        xpos 40 ypos 160
        idle Solid("#00000000")
        hover Solid("#00000000")
        xsize 180 ysize 220
        action clickPlant

    imagebutton:
        idle Solid("#00000000")
        hover Solid("#00000000")
        xpos 500 ypos 500
        xsize 210 ysize 130
        action clickRadio
    
    if len(curevidence) > 0:
        imagebutton:
            xpos 700 ypos 200
            idle "Folder_Closed.png"
            hover "Folder_Open_Paper.png"
            action clickFolder
    else:
        imagebutton:
            xpos 700 ypos 200
            idle "Folder_Closed.png"
            hover "Folder_Open.png"
            action clickFolder

    imagebutton:
        xpos 350 ypos 650
        idle "Notebook_Closed.png"
        hover "Notebook_Open.png"
        activate_sound "pencil.mp3"
        action clickNotebook

    imagebutton:
        xpos 1400 ypos 600
        idle "Binder_Closed.png"
        hover "Binder_Open.png"
        action clickBinder

    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"

    

screen show_news(report, img):
    text report:
        xpos 100
        ypos 250
        xsize 800
        ysize 800
        color "#000000"
    image img:
        xpos 1340
        ypos 230

screen show_supervisor:
    image "Door_Closed.png" xpos 1520 ypos 0
    image "Cabinet_Base.png" xpos -7 ypos 150
    
    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600

    image "Notebook_Closed.png" xpos 350 ypos 650
    image "Binder_Open.png" xpos 1400 ypos 600
    side "c b r":
        add Solid("#FFFFFF", xsize=650, ysize=850, xpos=-25, ypos=-25)
        area(660, 140, 600, 800)
    
        vbox:
            ysize 800
            text "Supervisor Note" color "#000000" ypos 35
            hbox:
                ysize 530
                viewport id "vp":
                    ysize 530
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    vbox:
                        xsize 580
                        xalign 0.5 yalign 0.0
                        spacing 10
                        text lastmemo color "#000000"
                        if curday == 2:
                            image "Car.png"
                
            textbutton "Return" action Jump("l_main")
    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"


# The game starts here.

screen show_background():
    image "Door_Closed.png":
        xpos 1520 ypos 0
        
    image "Cabinet_Base.png":
        xpos -7 ypos 150

    if numEvStored>EvLimit/4*3:
        image "Cabinet_Open_100.png" xpos -7 ypos 150
    elif numEvStored>EvLimit/2:
        image "Cabinet_Open_75.png" xpos -7 ypos 150
    elif numEvStored>EvLimit/4:
        image "Cabinet_Open_50.png" xpos -7 ypos 150
    elif numEvStored>0:
        image "Cabinet_Open_25.png" xpos -7 ypos 150
    else:
        image "Cabinet_Open.png" xpos -7 ypos 150 

    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600
    
    image "Folder_Closed.png":
        xpos 700 ypos 200

    image "Notebook_Closed.png":
        xpos 350 ypos 650

    image "Binder_Closed.png":
        xpos 1400 ypos 600

    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"


screen show_background2():
    image "Door_Closed.png":
        xpos 1520 ypos 0
        
    image "Cabinet_Base.png":
        xpos -7 ypos 150

    
    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600
    
    image "Folder_Closed.png":
        xpos 700 ypos 200

    image "Notebook_Open.png":
        xpos 350 ypos 650

    image "Binder_Closed.png":
        xpos 1400 ypos 600

    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"

            
screen show_char_file(name):
    image "Door_Closed.png" xpos 1520 ypos 0
    image "Cabinet_Base.png" xpos -7 ypos 150   
    if numEvStored>EvLimit/4*3:
        image "Cabinet_Open_100.png" xpos -7 ypos 150
    elif numEvStored>EvLimit/2:
        image "Cabinet_Open_75.png" xpos -7 ypos 150
    elif numEvStored>EvLimit/4:
        image "Cabinet_Open_50.png" xpos -7 ypos 150
    elif numEvStored>0:
        image "Cabinet_Open_25.png" xpos -7 ypos 150
    else:
        image "Cabinet_Open.png" xpos -7 ypos 150     
     
    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600
    image "Notebook_Closed.png" xpos 350 ypos 650
    image "Binder_Closed.png" xpos 1400 ypos 600 
    side "c b r":
        add Solid("#FFFFFF", xsize=850, ysize=850, xpos=-25, ypos=-25)
        area(560, 140, 800, 800)
        
        vbox:
            ysize 800
            text "Citizen Files \t\t\tEvidence Stored: "+str(numEvStored) +" / "+str(EvLimit) color "#000000" ypos -25
            hbox:
                ysize 700
                ypos 0
                viewport id "vp":
                    ysize 700
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    vbox:
                        xsize 800
                        xalign 0.5 yalign 0.0
                        spacing 10
                        $showCharacterFile(name)
                        #text notebook color "#000000"
                    
            textbutton "Return" action Jump("l_files")
    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"

screen show_arrest_info():
    if banksFree==True:
        text "You didn't detain him" xpos 220 ypos 350 color "#000000"
    elif suspects["Robert Banks"].status == "Arrested":
        text "You detained him" xpos 220 ypos 350 color "#000000"
    else:
        text "You didn't detain him" xpos 220 ypos 350 color "#000000"
    if suspects["Svetlana Brown"].status == "Arrested":
        text "You detained her" xpos 220 ypos 510 color "#000000"
    else:
        text "You didn't detain her" xpos 220 ypos 510 color "#000000"
    if eggFree==True:
        text "You didn't detain him" xpos 205 ypos 670 color "#000000"
    elif suspects["Walter Eggleston"].status == "Arrested":
        text "You detained him" xpos 205 ypos 670 color "#000000"
    else:
        text "You didn't detain him" xpos 205 ypos 670 color "#000000"
    if suspects["Margot Flossi"].status == "Arrested":
        text "You detained her" xpos 205 ypos 830 color "#000000"
    else:
        text "You didn't detain her" xpos 205 ypos 830 color "#000000"
    if suspects["Candace Green"].status == "Arrested":
        text "You detained her" xpos 905 ypos 350 color "#000000"
    else:
        text "You didn't detain her" xpos 905 ypos 350 color "#000000"
    if suspects["Terrence Ianson"].status == "Arrested":
        text "You detained him" xpos 905 ypos 510 color "#000000"
    else:
        text "You didn't detain him" xpos 905 ypos 510 color "#000000"
    if suspects["Steve Johnson"].status == "Arrested":
        text "You detained him" xpos 905 ypos 670 color "#000000"
    else:
        text "You didn't detain him" xpos 905 ypos 670 color "#000000"
    if suspects["Norman Pearson"].status == "Arrested":
        text "You detained him" xpos 905 ypos 830 color "#000000"
    else:
        text "You didn't detain him" xpos 905 ypos 830 color "#000000"
    if suspects["Georg Sieland"].status == "Arrested":
        text "You detained him" xpos 1530 ypos 355 color "#000000"
    else:
        text "You didn't detain him" xpos 1530 ypos 355 color "#000000"
    if suspects["Julia Smith"].status == "Arrested":
        text "You detained her" xpos 1530 ypos 515 color "#000000"
    else:
        text "You didn't detain her" xpos 1530 ypos 515 color "#000000"
    if suspects["Lorenzo Steeves"].status == "Arrested":
        text "You detained him" xpos 1530 ypos 675 color "#000000"
    else:
        text "You didn't detain him" xpos 1530 ypos 675 color "#000000"
    if suspects["Charlene Webber"].status == "Arrested":
        text "You detained her" xpos 1530 ypos 835 color "#000000"
    else:
        text "You didn't detain her" xpos 1530 ypos 835 color "#000000"

screen show_characters():
    image "Door_Closed.png" xpos 1520 ypos 0
    image "Cabinet_Base.png" xpos -7 ypos 150    
    if numEvStored>EvLimit/4*3:
        image "Cabinet_Open_100.png" xpos -7 ypos 150
    elif numEvStored>EvLimit/2:
        image "Cabinet_Open_75.png" xpos -7 ypos 150
    elif numEvStored>EvLimit/4:
        image "Cabinet_Open_50.png" xpos -7 ypos 150
    elif numEvStored>0:
        image "Cabinet_Open_25.png" xpos -7 ypos 150
    else:
        image "Cabinet_Open.png" xpos -7 ypos 150
    
    if curday == 1:
        image "Notes/Note_1.png":
            xpos 20 ypos 600
    elif curday < 4:
        image "Notes/Note_2.png":
            xpos 20 ypos 600
    elif curday < 6:
        image "Notes/Note_3.png":
            xpos 20 ypos 600
    elif curday < 8:
        image "Notes/Note_4.png":
            xpos 20 ypos 600
    else:
        image "Notes/Note_5.png":
            xpos 20 ypos 600

    image "Notebook_Closed.png" xpos 350 ypos 650
    image "Binder_Closed.png" xpos 1400 ypos 600
    side "c b r":
        add Solid("#FFFFFF", xsize=850, ysize=850, xpos=-25, ypos=-25)
        area(560, 140, 800, 800)
        
        vbox:
            ysize 800
            text "Citizen Files \t\t\tEvidence Stored: "+str(numEvStored) +" / "+str(EvLimit) color "#000000" ypos -25
            hbox:
                ysize 700
                ypos 0
                viewport id "vp":
                    ysize 700
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    vbox:
                        xsize 800
                        xalign 0.5 yalign 0.0
                        spacing 10
                        $showCharacterFiles()
                        #text notebook color "#000000"
                    
            textbutton "Return" action Jump("l_main")
    imagebutton:
        xpos 250 ypos 800
        idle "Calendar/Calendar_"+str(curday)+".png"


label start:
    play music "Melt.ogg"
    jump day1


label l_files:
    play sound "file_open.mp3"
    call screen show_characters()

label l_main:
    if (curday >= numdays) or (curday == numdays - 1 and suspects["Candace Green"].status == "Alive"):
        jump end
        
    $refreshClock()
    call screen buttons

label l_stored_main:
    show screen show_background
    $ renpy.pause(0.25)
    hide screen show_background
    $refreshClock()
    call screen buttons

label l_note:
    show screen show_background2
    $notebook.append(renpy.input("Enter Note:"))
    hide screen show_background2
    jump l_notebook

label l_news_free(char, report):
    scene bg news
    if suspects[char].status != "Arrested":
        show screen show_news(report, "Portaits_Big/" + char.replace(" ", "_") + ".png")
        pause
        hide screen show_news

    return

label l_binder:
    call screen show_supervisor(lastmemo)

label l_news_arrested:
    scene bg news
    python:

        for rep in arrestReports:
            renpy.show_screen("show_news", rep[0], rep[1])
            renpy.pause()
            renpy.hide_screen("show_news")

        arrestReports = []
    
    return

label l_next_ev:
    if len(curevidence) == 0:
        jump l_main

    play sound "paper.mp3"
    $ev = curevidence[0]
    $curevidence.pop(0)
    call screen show_newEvidence(ev, False)

label l_notebook:
    call screen show_notebook()

label l_char_file(char):
    call screen show_char_file(char)

label l_show_ev(file):
    play sound "paper.mp3"
    call screen show_newEvidence(file, True)

label l_arrest(susp):
    show screen show_background
    if susp in govtSuspects:
        menu:
            "Are you sure you want to report this supervisor?"

            "Yes":
                hide screen show_background
                $govtArrested = susp
                $arrest(susp)

            "No":
                hide screen show_background
                jump l_files
    else:
        menu:
            "Are you sure you want to detain this person?"

            "Yes":
                hide screen show_background
                $arrest(susp)

            "No":
                hide screen show_background
                jump l_files

label l_shredAll(char):
    show screen show_background
    menu:
        "Are you sure you want to shred all of this persons evidence?\nDoing so may remove the suspect from the filing cabinet."

        "Yes":
            hide screen show_background
            $removeAll(char)
        
        "No":
            hide screen show_background
            jump l_files

label l_nextDay:
    python:
        curevidence = []
        curday += 1
        if curday <= numdays:
            renpy.jump("day" + str(curday))

label play:
    $numEvidence = len(curevidence)
    $refreshClock()
    with fade
    play sound "tower_clock.ogg"
    call screen show_supervisor()

label day1:
    $addEvidence("Johnson_Jersey")
    $addEvidence("Banks_Gun")
    $storeMemo(["Day1"])
    jump play

label day2:
    call l_news_arrested() from _call_l_news_arrested
    $addEvidence("Johnson_Shopping")
    $addEvidence("Banks_Car")
    $storeMemo(["Day2"])
    jump play

label day3:
    call l_news_arrested() from _call_l_news_arrested_1
    call l_news_free("Robert Banks", nr_banks_free) from _call_l_news_free
    $addEvidence("Sieland_WifeCall")
    $addEvidence("Smith_Call")
    $addEvidence("Pearson_Gun_Stockpile")
    $addEvidence("Smith_Invoices")
    $storeMemo([("BanksNotArrested", "Robert Banks", "Alive"), "Day3"])
    python:
        if(suspects["Robert Banks"].status != "Arrested"):
            banksFree=True
    $suspects["Robert Banks"].status = "Arrested"
    jump play

label day4:
    call l_news_arrested() from _call_l_news_arrested_2
    $addEvidence("Sieland_CodeLetter")
    $addEvidence("Sieland_IntlStamps")
    $addEvidence("Pearson_Message_Drop")
    $addEvidence("Webber_Loitering")
    $addEvidence("Brown_AgentLetter")
    $storeMemo([("Sieland_NotArrested", "Georg Sieland", "Alive"), "Day4"])
    jump play

label day5:
    call l_news_arrested() from _call_l_news_arrested_3
    $addEvidence("Eggleston_Receipt")
    $addEvidence("Smith_Tickets")
    $addEvidence("Brown_Letter")
    $addEvidence("Webber_Taxes_Inc")
    $addEvidence("Brown_Call")
    $addEvidence("Eggleston_Gun_Receipt")
    $storeMemo(["Day5"])
    jump play

label day6:
    call l_news_arrested() from _call_l_news_arrested_4
    $addEvidence("Sieland_WifeCallKid")
    $addEvidence("Pearson_Supplies")
    $addEvidence("Smith_CreditCard")
    $addEvidence("Steeves_Purchase")
    $storeMemo(["Day6"])
    jump play

label day7:
    call l_news_arrested() from _call_l_news_arrested_5
    call l_news_free("Margot Flossi", nr_flossi_free) from _call_l_news_free_1
    $addEvidence("Sieland_FromMikie")
    $addEvidence("Eggleston_Call")
    $addEvidence("Webber_Bomb_Agent")
    $addEvidence("Green_Shopping")
    $addEvidence("Pearson_Phone_4AM")
    $addEvidence("Eggleston_TailLog")
    $storeMemo(["Day7"])
    jump play

label day8:
    call l_news_arrested() from _call_l_news_arrested_7
    call l_news_free("Charlene Webber", nr_webber_free) from _call_l_news_free_2
    $addEvidence("Green_Call")
    $addEvidence("Green_Call_Intl")
    $addEvidence("Ianson_Receipt")
    $addEvidence("Eggleston_Letter")
    $addEvidence("Steeves_IntlCall")
    $addEvidence("Smith_Tickets")
    $storeMemo(["Day8"])
    jump play

label day9:
    call l_news_arrested() from _call_l_news_arrested_8
    call l_news_free("Walter Eggleston", nr_eggleston_free) from _call_l_news_free_3
    $addEvidence("Flossi_Receipt")
    $addEvidence("Green_TailLog")
    $addEvidence("Ianson_TailLog")
    $addEvidence("Pearson_TailLog")
    $addEvidence("Flossi_Letter")
    $addEvidence("Ianson_Call")
    $storeMemo([("Eggleston_NotArrested", "Walter Eggleston", "Alive"), "Day9", ("Green_NAInfo", "Candace Green", "Alive")])
    python:
        if(suspects["Walter Eggleston"].status != "Arrested"):
            eggFree=True
    $suspects["Walter Eggleston"].status = "Arrested"
    jump play
   
label day10:
    $arrestReports.append((nr_green_arrested, "Portaits_Big/Candace_Green.png"))
    call l_news_arrested() from _call_l_news_arrested_6
    $addEvidence("King_InfoRequests")
    $addEvidence("OBrien_InfoRequests")
    $addEvidence("McDowell_InfoRequests")
    $storeMemo([("Day10", "Candace Green", "Arrested"), ("Green_NotArrested", "Candace Green", "Alive")])
    jump play

label day11:
    call l_news_arrested() from _call_l_news_arrested_9
    $storeMemo([("Day11", ["Charles O'Brien", "Wendy King", "Roland McDowell"], "Alive")])
    jump play

label end:
    scene bg ending
    show screen show_arrest_info
    $renpy.pause()
    hide screen show_arrest_info
    $renpy.quit()
