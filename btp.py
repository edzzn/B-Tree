
# coding: utf-8

# # B+Tree

# In[1]:


# El módulo abc obliga a las clases derivadas a implemtar
# un método particular utilizando @abstractmethod
from abc import ABCMeta, abstractmethod

# Permite trabajar mejor con listas, insertar conservando el orden
import bisect
from math import floor as floor


# In[2]:


class Node(metaclass=ABCMeta):  
    
    def __init__(self):
        self.num = 0
        self.keys = []
        
    @abstractmethod
    def getLoc(self, key):
        """Return null si no split. Si no retorna la info del split."""
        pass
    
    @abstractmethod
    def insert(self, key,value): pass
    
    @abstractmethod
    def display(self): pass


# In[3]:


class Split:
    
    # TODO: Refactor Split
    
    def __init__(self, key, node_leaf, node_right):
        self.key = key
        self.left = node_leaf
        self.right = node_right
    


# In[4]:


class LNode(Node):
    
    def __init__(self):
        super(LNode, self).__init__();
        
        self.values = []
    
    def getLoc(self, key):
         for i, key_i in enumerate(self.keys):
            if key_i >= key:
                return i
        # Si no se encontró una posición retorna la posición final
         return len(self.keys)
        #return bisect.bisect_left(self.keys, key)

            
    def insert(self, key, value):
        i = self.getLoc(key)
        
        if self.num == M:
            # Nodo llego, se debe dividir
            mid = floor((M + 1) / 2)
            sNum = self.num - mid
            
            # Creamos un nodo Hermano, y a este le asignamos la mitad de los elementos
            sibling = LNode()
            sibling.num = sNum

            sibling.keys = self.keys[mid:]
            sibling.values = self.values[mid:]
            self.keys = self.keys[:mid]
            self.values = self.values[:mid]
            self.num = mid
            
            if i < mid:
                self.insertNonFull(key, value, i)
            else:
                sibling.insertNonFull(key, value, i-mid)
                            
            # notificar al nodo padre
            result = Split(sibling.keys[0], self, sibling)
            
            return result
        
        else:
            self.insertNonFull(key, value, i)
            return None 
        
    def insertNonFull(self, key, value, i):
        #print("key: {}, val: {}, i: {}".format(key, value, i))
        self.keys.insert(i, key)
        self.values.insert(i, value)
        self.num += 1    
    
    def display(self):
        print('\t<LNode>\t', end='')
        
        for key, val in zip(self.keys, self.values):
            print("{} -> {}\t".format(key, val), end='')
        print('')
    
    def showChildren(self):
        print("Children: {}".format(len(self.values)))
        print("Children: {}".format(self.num))
        print("")


# In[5]:


class INode(Node):
    
    def __init__(self):
        super(INode, self).__init__();
                
        self.children = []
    
    def getLoc(self, key):
         for i, key_i in enumerate(self.keys):
            if key_i >= key:
                return i
        # Si no se encontró una posición retorna la posición final
         return len(self.keys)
        #return bisect.bisect_left(self.keys, key)
            
    def insert(self, key, value):        
        if self.num == N:
            # Dividir
            mid = floor((N + 1) / 2)
            sNum = self.num - mid
            
            sibling = INode()
            sibling.num = sNum
            
            sibling.keys = self.keys[mid:]
            sibling.children = self.children[mid:]
            
            self.keys = self.keys[:mid]
            self.children = self.children[:mid]
            self.num = mid - 1 # El elemento del extremo izq se envia a la parte superior
            
            result = Split(self.keys[mid-1], self, sibling)
            
            # insertar en el lado apropiado            
            if key < result.key: # menor que cero
                self.insertNonFull(key, value)
            else:
                sibling.insertNonFull(key, value)
            
            return result
        
        else:
            self.insertNonFull(key, value)
            return None
        
    def insertNonFull(self, key, value):
        i = self.getLoc(key)
        result = self.children[i].insert(key, value)
        
        if result is not None:
            # Caso contrario no se debe modicar nada
            
            if i == self.num:
                # Insertamos a la derecha
                
                #self.keys[i] = result.key
                #self.children[i] = result.left
                #self.children[i+1] = result.right


                self.keys.insert(i, result.key)
                self.children.insert(i, result.left)
                self.children.insert(i+1, result.right)
                
                self.num += 1
                
            else:
                self.children = self.children[:] + [result.left]
                self.children = self.children[:i+1] + [result.right]
                self.keys.insert(i, result.key)
                self.num += 1;              
        
    def display(self):
        print("Displaying INode")

        print('<INode>\t', end='')

        for key in self.keys:
            print('{}\t'.format(key), end='')
        print("")       

        for child in self.children:
            if isinstance(child, INode):
                print("")
            child.display()
    
    def showChildren(self):
        print("Children INode: {}".format(len(self.children)))
        print("Children INode: {}".format(self.num))
        self.display()
        print("")    


# In[6]:


class BTree:
    
    def __init__(self, degree):
        self.max_leafs = degree - 1
        self.max_inner_nodes = degree
        
        M = self.max_leafs
        N = self.max_inner_nodes
        
        self.root = LNode()
    
    def insert(self, key, value):

        #print("BEFORE ADD")
        #self.root.showChildren()
        
        print("Insertar [{}]={}".format(key, value))
        result = self.root.insert(key, value)
        
        if result is not None:
            # Se dividió la raiz
            # Se crea una nueva raiz
            _root = INode()
            _root.num = 2
            _root.keys.insert(0, result.key)           
            _root.children.insert(0, result.left)
            _root.children.insert(1, result.right)
            self.root = _root
            
        #print("AFTER ADD")
        #self.root.showChildren()
        #print("")
        #print("- - -")
        #print("")
    
    def find(self, key):
        node = self.root
        
        while isinstance(node, INode):
            idx = node.getLoc(key)
            node = node.children[idx]
        
        # Estamos en la hoja
        idx = node.getLoc(key)
        
        if idx < node.num and node.keys[idx] == key:
            return node.values[idx]
        else:
            return None
    
    def display(self):
        self.root.display()


# In[7]:


tree = BTree(3)


# In[8]:


# Maximo número de hojas
M = 2;

# Maximo número de nodos en nodo intermedio
N = 3;


# In[9]:


tree.insert(1, "1111")


# In[10]:


tree.insert(2, "2222")


# In[11]:


tree.insert(4, "4444")


# In[12]:


tree.insert(3, "3333")


# In[13]:

tree.display()



tree.insert(7, "7777")
tree.insert(6, "6666")

tree.insert(5, "5555")


print("")
tree.display()
