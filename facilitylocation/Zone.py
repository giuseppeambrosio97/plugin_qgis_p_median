class Zone:
    """
        Variabili d'istanza:
        id (int): id identificativo associato all'istanza
        geometry (QgsPointXY): coordinate (longitudine,latitudine) associate all'istanza
    """
    def __init__(self, id, geometry):
       self.id = id
       self.geometry = geometry
    
    def __str__(self):
        return 'id  = {}, geometry = {}'.format(self.id,self.geometry)