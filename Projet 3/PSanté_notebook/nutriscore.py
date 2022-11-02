def point_A_energy_general(n):
    if n <= 335:
        return 0
    elif 335 < n <= 670:
        return 1
    elif 670 < n <= 1005:
        return 2
    elif 1005 < n <= 1340:
        return 3
    elif 1340 < n <= 1675:
        return 4
    elif 1675 < n <= 2010:
        return 5
    elif 2010 < n <= 2345:
        return 6
    elif 2345 < n <= 2680:
        return 7
    elif 2680 < n <= 3015:
        return 8
    elif 3015 < n <= 3350:
        return 9
    elif 3350 < n:
        return 10


def point_A_sugars_general(n):
    if n <= 4.5:
        return 0
    elif 4.5 < n <= 9:
        return 1
    elif 9 < n <= 13.5:
        return 2
    elif 13.5 < n <= 18:
        return 3
    elif 18 < n <= 22.5:
        return 4
    elif 22.5 < n <= 27:
        return 5
    elif 27 < n <= 31:
        return 6
    elif 31 < n <= 36:
        return 7
    elif 36 < n <= 40:
        return 8
    elif 40 < n <= 45:
        return 9
    elif 45 < n:
        return 10


def point_A_energy_beverage(n):
    if n <= 0:
        return 0
    elif 0 < n <= 30:
        return 1
    elif 30 < n <= 60:
        return 2
    elif 60 < n <= 90:
        return 3
    elif 90 < n <= 120:
        return 4
    elif 120 < n <= 150:
        return 5
    elif 150 < n <= 180:
        return 6
    elif 180 < n <= 210:
        return 7
    elif 210 < n <= 240:
        return 8
    elif 240 < n <= 270:
        return 9
    elif 270 < n:
        return 10


def point_A_sugars_beverage(n):
    if n <= 0:
        return 0
    elif 0 < n <= 1.5:
        return 1
    elif 1.5 < n <= 3:
        return 2
    elif 3 < n <= 4.5:
        return 3
    elif 4.5 < n <= 6:
        return 4
    elif 6 < n <= 7.5:
        return 5
    elif 7.5 < n <= 9:
        return 6
    elif 9 < n <= 10.5:
        return 7
    elif 10.5 < n <= 12:
        return 8
    elif 12 < n <= 13.5:
        return 9
    elif 13.5 < n:
        return 10



def point_A_fat_general(n):
    if n <= 1:
        return 0
    elif 1 < n <= 2:
        return 1
    elif 2 < n <= 3:
        return 2
    elif 3 < n <= 4:
        return 3
    elif 4 < n <= 5:
        return 4
    elif 5 < n <= 6:
        return 5
    elif 6 < n <= 7:
        return 6
    elif 7 < n <= 8:
        return 7
    elif 8 < n <= 9:
        return 8
    elif 9 < n <= 10:
        return 9
    elif 10 < n:
        return 10


def point_A_fat_fat(n):
    if n <= 10:
        return 0
    elif 10 < n <= 16:
        return 1
    elif 16 < n <= 22:
        return 2
    elif 22 < n <= 28:
        return 3
    elif 28 < n <= 34:
        return 4
    elif 34 < n <= 40:
        return 5
    elif 40 < n <= 46:
        return 6
    elif 46 < n <= 52:
        return 7
    elif 52 < n <= 58:
        return 8
    elif 58 < n <= 64:
        return 9
    elif 64 < n:
        return 10


def point_A_sodium(n):
    if n <= 90:
        return 0
    elif 90 < n <= 180:
        return 1
    elif 180 < n <= 270:
        return 2
    elif 270 < n <= 360:
        return 3
    elif 360 < n <= 450:
        return 4
    elif 450 < n <= 540:
        return 5
    elif 540 < n <= 630:
        return 6
    elif 630 < n <= 720:
        return 7
    elif 720 < n <= 810:
        return 8
    elif 810 < n <= 900:
        return 9
    elif 900 < n:
        return 10


def point_C_fruits_vegetables_general(n):
    if n <= 40:
        return 0
    elif 40 < n <= 60:
        return 1
    elif 60 < n <= 80:
        return 2
    elif 80 < n:
        return 5


def point_C_fruits_vegetables_beverage(n):
    if n <= 40:
        return 0
    elif 40 < n <= 60:
        return 2
    elif 60 < n <= 80:
        return 4
    elif 80 < n:
        return 10


def point_C_fiber(n):
    if n <= 0.7:
        return 0
    elif 0.7 < n <= 1.4:
        return 1
    elif 1.4 < n <= 2.1:
        return 2
    elif 2.1 < n <= 2.8:
        return 3
    elif 2.8 < n <= 3.5:
        return 4
    elif 3.5 < n:
        return 5


def point_C_proteins(n):
    if n <= 1.6:
        return 0
    elif 1.6 < n <= 3.2:
        return 1
    elif 3.2 < n <= 4.8:
        return 2
    elif 4.8 < n <= 6.4:
        return 3
    elif 6.4 < n <= 8:
        return 4
    elif 8 < n:
        return 5


def compute_nutriscore(x):
    point_A = 0

    if x['is_beverage']:
        point_A += point_A_energy_beverage(x['_energy_100g'])
        point_A += point_A_sugars_beverage(x['sugars_100g'])
    else:
        point_A += point_A_energy_general(x['_energy_100g'])
        point_A += point_A_sugars_general(x['sugars_100g'])
    
    if x['is_fat']:
        point_A += point_A_fat_fat(x['saturated-fat_100g'])
    else:
        point_A += point_A_fat_general(x['saturated-fat_100g'])
    
    point_A += point_A_sodium(x['sodium_100g'])

    if x['is_beverage']:
        _point_C_fruits_vegetables = point_C_fruits_vegetables_beverage(x['fruits-vegetables-nuts-estimate-from-ingredients_100g'])
    else:
        _point_C_fruits_vegetables = point_C_fruits_vegetables_beverage(x['fruits-vegetables-nuts-estimate-from-ingredients_100g'])
    
    _point_C_fiber = point_C_fiber(x['fiber_100g'])
    _point_C_proteins = point_C_proteins(x['proteins_100g'])

    point_C = _point_C_fruits_vegetables + _point_C_fiber + _point_C_proteins

    if point_A < 11 or x['is_cheese']:
        return point_A - point_C
    else:
        if _point_C_fruits_vegetables == 5:
            return point_A - point_C
        else:
            return point_A - (_point_C_fiber + _point_C_fruits_vegetables)
