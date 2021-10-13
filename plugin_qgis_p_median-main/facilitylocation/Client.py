class Client:
    """
        Variabili d'istanza:
        id (int): id identificativo associato all'istanza
        weight (float): peso associato all'istanza
        geometry (QgsPointXY): coordinate (longitudine,latitudine) associate all'istanza
        zone (Zone): istanza Zone in cui l'istanza Client si approvvigiona
    """
    def __init__(self, id, weight, geometry):
        self.id = id
        self.weight = weight
        self.geometry = geometry
    
    def link_to_zone(self,zone):
        self.zone = zone
    
    def __str__(self):
        return 'id  = {}, weight = {}, geometry = {}, zone = {}'.format(self.id,self.weight,self.geometry,self.zone)