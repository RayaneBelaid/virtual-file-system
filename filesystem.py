import sys
import os


#########################################################################################################
# Class: FileSystem                                                                                     #
# Objectif : implémenter les fonctions pour les opérations nécessaires pour la gestion des fichiers.    #                                                                                            
#########################################################################################################
class FileSystem():
    BLOCK_SIZE  = 512   #la taille du block
    BLOCK_NUM   = 1000  #nombre de blocks
    
    #inode map: a table indicating where each inode is on the disk
    #inode map blocks are written as part of the segment; a table in a fixed checkpoint region on disk points to those blocks
    #inode map: une table qui indique l'emplacement de chaque inode dans le disque
    INODE_MAP   = [x for x in range(0, 80 // 8)] #[0-9]
    INODE_BLOCK = [x for x in range(1, 81)]  #[1-81]
    
    def __init__(self):
        #récuperer le chemin du répertoire 
        fspath = os.getcwd() + '/' + "vsf"
        print(fspath)
        #Vérifier s'il exite
        if False == os.path.exists(fspath): 
            print("Info: système de fichier n'existe pas, reconstruction")
            #ouverture du fichier(image disque) en mode écriture sur lequel on va stocké les informations de notre système de fichier
            self.fs = open("vsf", "w+")ls
                         
            #La technique bitmap permet de trouver rapidement un emplacement libre sur la table des inodes(ou sur les blocks de donees) 
            #lors de la modification sur le système de fichier
            
            #Initialisation des données 
            initData = (chr(0x80) + chr (0x00) * self.INODE_MAP[-1] + #iNode bitmap 
                chr(0x80) + chr(0x00) * (self.BLOCK_SIZE - len(self.INODE_MAP) - 1) +  #data bitmap
                'D' + chr(0x00) + chr(len(self.INODE_BLOCK) + 1) + chr(0x00) * (self.BLOCK_SIZE - 3) + #iNode pour "/"
                chr(0x00) * self.BLOCK_SIZE * (len(self.INODE_BLOCK) - 1) + #autres inodes
                chr(0x00) * self.BLOCK_SIZE * (self.BLOCK_NUM - len(self.INODE_BLOCK) - 1) #blocks de donnees
                )
            #Ecriture sur le système de fichier    
            self.fs.write(initData)
            #Fermeture  du système de fichier
            self.fs.close()
        
        #si le système de fichier existe
        else:
            print("Info: système de fichier existe, importation")

        self.data = []
        self.__load()
        self.dataStart = self.BLOCK_SIZE * (len(self.INODE_BLOCK) + 1) #512*82 la taille des blocs
        self.curDir = "/"
        self.curInode = self.__getInode(0)
        

    #spprimer le système de fichier
    def __del__(self):
        self.__save()
        self.fs.close()

    #Importer le système de fichier
    def __load(self):
        self.fs = open("vsf", "r+")
        self.data = list(self.fs.read())
        self.fs.close()

     #sauvegarder le système de fichier 
    def __save(self):
        #initilize data
        self.data = []
        data = "".join(self.data)
        self.fs = open("vsf", "w+")
        self.fs.write(data)
        self.fs.close()


    def __lookup(self):
        pass


    def __find(self, path):
        pass

    # verifier l'image bitmap
    def checkMap(self):
        line = ""
        for x in range(0, self.BLOCK_SIZE):
            byte = self.data[x]
            if x % 5 == 0:
                print(line)
                line = ""
            if x == len(self.INODE_MAP) or x == self.BLOCK_SIZE:
                print("")
            for y in range(0, 8):
                line += str((ord(byte) >> (7 - y)) & 0x01)
            line += " "

    #créer un nouveau inode
    def __newInode(self, itype):
        for x in range(0, len(self.INODE_MAP)):
            #recuperer un bit de bitmap
            byte = self.data[x]
            for y in range(0, 8):  #range() = returns a sequence of numbers, starting by 0 by default and increment by 1 by default, and stops before specified number
                #verifier s'il est = 0 pour creer un nouv inode
                if ((ord(byte) >> (7 - y)) & 0x01) == 0:  #ord() returns an intiger representing the unicode character
                    print("Info: nouveau inode " + str(x * 8 + y))
                    self.data[x] = chr(ord(byte) | (0x80 >> y))
                    self.__initInode(x * 8 + y, itype)
                    return x * 8 + y 
        return -1

    #supprimer un inode
    def __delInode(self, no):
        x = no // 8
        self.data[x] = chr(ord(self.data[x]) & (~(0x80 >> no % 8)) % 256)
        self.__initInode(no, chr(0x00))
        print("Info: supprimer l'inode " + str(no))
 
    #initialiser un inode 
    def __initInode(self, no, itype):
        inode = []
        for x in range(0, self.BLOCK_SIZE):
            inode += [chr(0x00)]
        inode[0] = itype

        if itype == 'D': #si le itype = D donc il s'agit d'une directorie/rep
            #création d'un nouveau block
            blockNum = self.__newBlock()
            inode[1] = chr(blockNum // 256)
            inode[2] = chr(blockNum % 256)
         #insérer sur l'inode   
        self.__writeInode(no, inode)

    #récupérer un inode
    def __getInode(self, no):
        inode = []
        #récupérer une tranche 512-1024
        inode = self.data[self.BLOCK_SIZE * (1 + no) : self.BLOCK_SIZE * (2 + no)] 
        return inode

    #insérer un inode
    def __setInode(self, no, itype, length, blocks):
        start = self.BLOCK_SIZE * (1 + no)

        self.data[start + 0] = itype
        
        if(itype == 'F'): #il s'agit d'un fichier 
            self.data[start + 1] = chr(length // 256)
            self.data[start + 2] = chr(length % 256)
            offset = 2
        else:
            offset = 0

        for x in range(0, len(blocks)):
            block = blocks[x]
            self.data[start + offset + x * 2 + 1] = chr(block // 256)
            self.data[start + offset + x * 2 + 2] = chr(block % 256)

    #insérer dans l'inode 
    def __writeInode(self, no, data):
        self.data[self.BLOCK_SIZE * (1 + no):self.BLOCK_SIZE * (2 + no)] = list(data)

    #créer un nouveau block
    def __newBlock(self):
        for x in range(len(self.INODE_MAP), len(self.INODE_MAP) + self.BLOCK_SIZE):
            byte = self.data[x]
            for y in range(0, 8):
                if ((ord(byte) >> (7 - y)) & 0x01) == 0:
                    print("Info: nouveau block " + str(x * 8 + y + 1))
                    self.data[x] = chr(ord(byte) | (0x80 >> y))
                    self.__initBlock(x * 8 + y + 1)
                    return x * 8 + y + 1
        return -1

    #supprimer un block
    def __delBlocks(self, nos):
        for no in nos:
            x = no // 8
            self.data[x] = chr(ord(self.data[x]) & (~(0x80 >> no % 8) % 256))
            self.__initBlock(no)
            print("Info: supprimer le block " + str(no))

    #initilaliser un block
    def __initBlock(self, no):
        for x in range(0, self.BLOCK_SIZE):
            self.data[self.dataStart + no * self.BLOCK_SIZE + x] = chr(0x00)

    #récupérer un block
    def __getBlocks(self, inode):
        blocks = inode[1:]
        listbn = []
        #print blocks
        if inode[0] == 'F': #si la valeur de indoe[0] = 'F' donc il s'agit d'un fichier 
            offset = 2
        else:
            offset = 0
        for x in range(0, (self.BLOCK_SIZE - 1) // 2):
            blockNo = (ord(blocks[x * 2 + offset]) << 7) + ord(blocks[x * 2 + 1 + offset])
            if blockNo == 0:
                return listbn
            else:
                listbn += [blockNo]
        return listbn

    #lire un block
    def __readBlocks(self, nos):
        return_data = []
        print("Lire inodes: " + str(nos))
        for no in nos:
            return_data += (self.data[no * self.BLOCK_SIZE :
                                no * self.BLOCK_SIZE + self.BLOCK_SIZE])
        #print str(len(return_data))
        return return_data

    #écrire un block
    def __writeBlocks(self, nos, datas):
        if len(datas) < self.BLOCK_SIZE * len(nos):
            for x in range(len(datas), self.BLOCK_SIZE * len(nos)):
                datas += chr(0x00)

        for x in range(0, len(nos)):
            no = nos[x]
            self.data[no * self.BLOCK_SIZE : 
                      no * self.BLOCK_SIZE + self.BLOCK_SIZE] = datas[x * self.BLOCK_SIZE : (x + 1) * self.BLOCK_SIZE]

    #récupérer la liste
    def __getList(self, inode):
        lists = self.__readBlocks(self.__getBlocks(inode))
        
        lists = "".join(lists).strip().split('\n')
        listDir = {}

        if inode[0] == 'D': #si la valeur de inode[0] =='D' donc il s'agit d'une dirèctorie
            for l in lists:
                if ord(l[0]) != 0x00:
                    name  = l.split(':')[0]
                    inode = int(l.split(':')[1])
                    listDir.update({name:inode})

        return listDir

    #insérer la liste
    def __setList(self, inode, newList):
        lists = ""
        for key in newList.keys():
            lists += (str(key) + ":" + str(newList[key]) + "\n")
        lists = list(lists)
        self.__writeBlocks(self.__getBlocks(inode), lists)

    #ouvrir un fichier s'il n'existe pas il sera créer
    def open(self, path):
        if path[0] != '/':
            #récupérer le chemin
            path = self.curDir + '/' + path
        #récupérer l'inode 
        inode    = self.__getInode(0)
        #initialiser le numéro de l'inode à 0
        inodeNum = 0
        if path == '/':
            return inodeNum, inode
        #récupérer le chemin 
        nods = path.split('/')[1:]
        #ré
        listDir  = self.__getList(inode)
        for nod in nods[:-1]:
            for key in listDir.keys():
                if str(nod) == str(key):
                    inode    = self.__getInode(listDir[key])
                    inodeNum = listDir[key]
                    listDir = self.__getList(inode)

        found = False
        nod = nods[-1]
        for key in listDir.keys():
            if str(nod) == str(key):
                inode    = self.__getInode(int(listDir[key]))
                inodeNum = int(listDir[key])
                found    = True
        #fichier n'exite pas    
        if found == False: # création du fichier
            print("Info: Le fichier " + nod + " n'existe pas, création")
            #créer un nouveau inode
            inodeNum = self.__newInode('F')
            #insérer le numéro de l'inode dans la listDir 
            listDir.update({nod:str(inodeNum)})
            #insrérer le nouveau inode et son numéro dans la liste 
            self.__setList(inode, listDir)
            #récupérer le numéro de l'inode 
            inode = self.__getInode(inodeNum)
        #retourner l'inode et son numéro    
        return inodeNum, inode

    #fermer le fichier/rep
    def close(self):
        pass

    #lire dans un répertoire
    def read(self, inodeNum):
        #récupérer l'inode
        inode = self.__getInode(inodeNum)
        if inode[0] != 'F': #s'il est différent de F donc il s'agit pas d'un fichier
            print("Erreur: Impossible de lire le répertoire")
            return []
        else:     
            #calculer la taille du fichier
            length = (ord(inode[1]) << 8) + ord(inode[2])
            #afficher la taille du fichier 
            print("La taille du fichier: " + str(length))
            #récupérer les données du fichier
            data   = self.__readBlocks(self.__getBlocks(inode))[:length]
            return list(data)

    #écrire sur un répertoire
    def write(self, inodeNum, data):
        #print "write: " + str(inodeNum)
        inode = self.__getInode(inodeNum)
        #print inode[0]
        if inode[0] != 'F': #s'il est différent de F donc il s'agit pas d'un fichier
            print("Erreur: Impossible d'écrir sur le répertoire ")
            return -1
        else:
            #insérer la nouvelle donnée dans la liste
            data   = list(data)
            #calculer la taille de ces données
            length = len(data)
            #récupérer le block occupés par ce répertoire
            blocks = self.__getBlocks(inode)
            #print blocks
            while length > len(blocks) * self.BLOCK_SIZE:
                #créer un nouveau block
                newBlock = self.__newBlock()
                if newBlock == -1:
                    print("Erreur: espace insuffisant")
                    return -2
                blocks += [newBlock]
            #écrire la nouvelle donnée sur le block 
            self.__writeBlocks(blocks, data)
            #insérer dans l'inode le nouveau block et la taille de la donnée
            self.__setInode(inodeNum, 'F', length, blocks)
            return 0

    #copier et déplacer un fichier
    def cp(self, src, dst):
        if src[0] != '/':
            src = self.curDir + '/' + src
        if dst[0] != '/':
            dst = self.curDir + '/' + dst
        #ouvrir le fichier source 
        inumSrc, nodeSrc = self.open(src)
        #ouvrir le fichier destination
        inumDst, nodeDst = self.open(dst)
        #lire le fichier source
        data = self.read(inumSrc)
        #ecrir sur le fichier distination
        self.write(inumDst, data)
         
        self.close() # not defined

    #suppression d'un fichier
    def rm(self, name):
        #récupérer la liste des répertoires
        listDir = self.__getList(self.curInode)

        for key in listDir.keys():
            if str(key) == name:
                inodeNum = listDir[key]
                #récupérer l'inode
                inode    = self.__getInode(inodeNum)
                if inode[0] == 'D': #si la valeur de inode[0] == 'D' donc il s'agit d'une directorie/répertoire
                    print("Erreur: Il n'est pas possible de supprimer ce répertoire, utilisez rmdir")
                    return -1
                #supprimer les blocks occupés par ce fichier 
                self.__delBlocks(self.__getBlocks(inode))
                #supprimer l'inode occupés par ce fichier
                self.__delInode(inodeNum)
                del listDir[key]
                self.__setList(self.curInode, listDir)
                print("Info: " + name + " removed")
                return 0

        print("Erreur: ce fichier n'existe pas")
        return -1


    #changer le répertoire
    def cd(self, name):
        #récupérer l'inode
        pnod    = self.curInode
        #récupérer la liste des répertoires
        listDir = self.__getList(pnod)

        if name == "..":
            self.curDir = "/".join(self.curDir.split('/')[:-1])

            if len(self.curDir) == 0:
                self.curDir = '/'
            inodeNum, self.curInode = self.open(self.curDir)
            return 0
            #print pnod
        
        #si le nom du ficher/rep n'est pas dans la liste des répertoires
        if name not in listDir.keys():
            print("Erreur: Ce répertoire n'existe pas")
            return -1
        else:
            if self.curDir[-1] != '/':
                path = (self.curDir + "/" + name)
            else:
                path = self.curDir + name
            inode = self.__getInode(listDir[name])
            if inode[0] != 'D':
                print("Erreur: impossible d'accéder à ce fichier")
                return -1
            else:
                self.curDir = path
                self.curInode = inode
                return 0
            #print self.curInode
        return -1

    #afficher les fichiers/répertoires
    def ls(self):
        #récupérer la liste des répertoires existants
        flist = self.__getList(self.curInode)
        #print flist
        result = []
        for key in flist.keys():
            result += [str(key)]
        return result

    #création de répertoire
    def mkdir(self, name):
        #récupérer l'inode
        pnod = self.curInode
        #récupérer la liste des répertoires
        listDir = self.__getList(pnod)
       #vérifier si le répertoire à créer existe dans la liste 
        if name in listDir.keys():
            print("Erreur: Le répertoire " + name + " existe déjà, impossible de le crée")
        else: #s'il n'existe pas, création
            #créer un nouveau inode
            inodeNum = self.__newInode('D')
            #ajout de nouveau répertoire dans la liste des répertoires
            listDir.update({name:inodeNum})
            self.__setList(pnod, listDir)

    #supprimer le répertoire      
    def rmdir(self, name):
        #récuperer la liste des répertoires 
        listDir = self.__getList(self.curInode)

        for key in listDir.keys():
            if str(key) == name:
                inodeNum = listDir[key]
                inode    = self.__getInode(inodeNum)
                if inode[0] == 'F': #s'il s'agit d'un fichier on utilise rm
                    print("Erreur: Il n'est pas possible de supprimer ce répertoire, utilisez rm")
                    return -1
                #récupérer le répertoire 
                listDel = self.__getList(inode)
                oldDir  = self.curDir
                self.curDir = self.curDir + '/' + name
                self.cd(name)
                for dkey in listDel.keys():
                    self.rm(str(dkey))
                self.cd("..")

                self.curDir = oldDir
                #supprimer les blocks utilisés par ce répertoire
                self.__delBlocks(self.__getBlocks(inode))
                #supprimer l'inode de ce répertoire
                self.__delInode(inodeNum)
                #supprimer ce répertoire de la liste 
                del listDir[key]
                self.__setList(self.curInode, listDir)
                print("Info: Le répertoire " + name + " à été supprimé")
                return 0

        print("Erreur: ce répertoire n'éxiste pas")
        return -1


#########################################################################################################
# Fonction: cmd (main)                                                                                  #
# Objectif : Cette fonction joue le role de simulateur de la boite de commandes pour tester             #
#            tous les opérations du système de fichier implémentés.                                     #                                                                                            
#########################################################################################################

def cmd():
    #appel le système de fichier
    fs = FileSystem()
    #récupérer l'inode
    inode = fs.curInode
    inodeNum = 0
    #initiliser la liste des commandes à utilisés
    helpInfo = "read, close, ls, check, quit, open, cd, mkdir, write, rm, rmdir, cp"
    while True:
        #recuperer le rep actuelle  
        c = input(fs.curDir + " >> ") 
        params = c.strip().split() #split = split a string into a list 
        #strip = remove any space from the beginning and from the end
        
        # si la requette à un seul paramètre
        if len(params) == 1:
            if params[0] == 'help':
                print(helpInfo) #afficher la liste des commendes
                continue

            if params[0] == 'read':
                print("".join(fs.read(inodeNum))) #join() = join all items in a tuples into one string
                continue
            
            if params[0] == 'close':
                inodeNum = 0
                continue

            if params[0] == 'ls':
                ls = fs.ls()
                for f in ls:
                    print(f)
                continue
            #vérifier le bitmap
            if params[0] == 'check':
                fs.checkMap()
                continue

            if params[0] == 'quit':
                break
        #si la requette a deux paramètres
        if len(params) == 2:
            if params[0] == 'open':
                inodeNum, inode = fs.open(params[1])
                continue

            if params[0] == 'cd':
                fs.cd(params[1])
                continue

            if params[0] == 'mkdir':
                fs.mkdir(params[1])
                continue

            if params[0] == 'write':
                fs.write(inodeNum, params[1])
                continue

            if params[0] == 'rm':
                fs.rm(params[1])
                continue

            if params[0] == 'rmdir':
                fs.rmdir(params[1])
                continue
        #si la requette a trois paramètres  
        if len(params) == 3:
            if params[0] == 'cp':
                fs.cp(params[1], params[2])
                continue

        #si la commande est introuvable
        print("Erreur: commande inconnu")
        print(helpInfo)



if __name__ == "__main__":
    cmd()