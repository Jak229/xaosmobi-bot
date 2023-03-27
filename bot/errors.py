class ItemHasMaxQualityLevel(Exception):
    def __init__(self, mes: str = "This item has max quality level"):
        super().__init__(mes)
