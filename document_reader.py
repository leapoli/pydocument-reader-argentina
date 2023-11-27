# -*- coding: utf-8 -*-
from enum import Enum
from re import search, match, sub


class TipoDocumento(Enum):
    CONDUCTOR = "Carnet de conductor"
    DNI_GEN_1 = "DNI generación 1"
    DNI_GEN_2 = "DNI generación 2"
    DNI_GEN_3 = "DNI generación 3"


class Document(object):
    """
    Clase contenedora de datos procesados en función de la lectura del documento.
    Incorpora una variable teclado_interpretado, para retornar cómo se entendió la cadena provista

        CC: Carnet conductor
        DNI1: DNI tarjeta generación 1
        DNI2: DNI tarjeta generación 2

    Modelo de datos y dónde pueden ser hallados:

        Tipo documento leído (DNI, carnet, etc): CC, DNI1, DNI2
        Tipo documento identidad (tipo de DNI): CC
        Nro dni: CC, DNI1, DNI2
        Sexo: CC, DNI1, DNI2
        Nombres: CC, DNI1, DNI2
        Apellidos: CC, DNI1, DNI2
        Fecha nac: CC, DNI1, DNI2
        Pais: CC
        Domicilio calle: CC
        Domicilio nro: CC
        Domicilio piso: CC
        Domicilio depto: CC
        Domicilio barrio: CC
        Ciudad: CC
        Código postal: CC
        Fecha emisión: CC, DNI2
        Fecha vencimiento: CC, DNI1
        Grupo y factor: CC
        Categoría conductor: CC
        Nro trámite: CC, DNI1, DNI2
        Of. ident: DNI1, DNI2 (no leído)
        Ejemplar: DNI1, DNI2

    Notas:

        - DNI gen. 3 tiene un campo sin identificar al final de la fecha de emisión en el valor leído. Caso Lucas: valor 2
        - DNI gen. 3 tiene un campo en la tarjeta "Of. ident." con un valor numérico de al menos 4 dígitos  
        - DNI gen. 1 y 2 tienen campos sin identificar en los valores leídos
  
    Muestra de carnet de conductor con teclado US:

        DNI
        23539652
        M
        JAVIER GUSTAVO RAMON
        SEGOVIA
        11-08-1974
        ARGENTINA
        LUCIO MANSILLA
        N 2072
        PisoÑ \'\'\'
        DeptoÑ \'\'\'
        BarrioÑ \'\'\'
        PARANA
        3100
        22-08-2018
        22-08-2023
        Bñ
        A ¿
        123631787

    Muestra carnet de conductor con teclado ES:  

        DNI
        23539652
        M
        JAVIER GUSTAVO RAMON
        SEGOVIA
        11/08/1974
        ARGENTINA
        LUCIO MANSILLA
        N 2072
        Piso: ---
        Depto: ---
        Barrio: ---
        PARANA
        3100
        22/08/2018
        22/08/2023
        B;
        A +
        123631787

    """
    carnet_conductor_us = "".join(("^DNI\n",
                                   "[0-9]{7,9}\n",
                                   "[A-Z]{1}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\n",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}){0,}\n",
                                   "([N][0-9]{1,}){0,}\n",
                                   # TODO No matchea para las palabras constantes con teclado US. Se usa el comodín en esa parte.
                                   "*",
                                   "Piso(.*)\n",
                                   "Depto(.*)\n",
                                   "Barrio(.*)\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}){0,}\n",
                                   "[0-9]{1,}\n",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\n",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\n",
                                   "[A-Z]([^\n]*)\n",
                                   "[A-Z]([^\n]*)\n",
                                   "[0-9]{1,}"))

    carnet_conductor_es = "".join(("^DNI\n",
                                   "[0-9]{7,9}\n",
                                   "[A-Z]{1}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\n",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}){0,}\n",
                                   "([N][\s][0-9]{1,}){0,}\n",
                                   "Piso:(.*)\n",
                                   "Depto:(.*)\n",
                                   "Barrio:(.*)\n",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\'\.°0-9]{1,}){0,}\n",
                                   "[0-9]{1,}\n",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\n",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\n",
                                   "[A-Z]([^\n]*)\n",
                                   "[A-Z]([^\n]*)\n",
                                   "[0-9]{1,}"))

    """
    Muestra de DNI tarjeta generación 3 con teclado US:

        00342157442"HERRMANN"LUCAS EMILIO"M"35296844"A"16-09-1990"06-02-2015"208

    Muestra de DNI tarjeta generación 3 con teclado ES:

        00342157442@HERRMANN@LUCAS EMILIO@M@35296844@A@16/09/1990@06/02/2015

    Existen casos donde se encuentran datos al final de la fecha de emisión. Los mismos son desestimados.

    Existen casos donde hay un error en la vocal acentuada, y en su lugar hay un caracter incorrecto. Los casos son:

        · Caso {
        
            00694683548@ARANDA@BRISA BEL{EN GABRIELA@F@41910327@D@21/06/1999@30/09/2022@271

    """
    dni_gen_tres_us = "".join(("[0-9]{1,}\"",
                               "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}){0,}\"",
                               "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}){0,}\"",
                               "[A-Z]{1}\"",
                               "[0-9]{7,9}\"",
                               "[A-Z]{1}\"",
                               "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                               "[0-9]{2}[-][0-9]{2}[-][0-9]{4}"))

    dni_gen_tres_es = "".join(("[0-9]{1,}@",
                               "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}){0,}@",
                               "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ{\']{1,}){0,}@",
                               "[A-Z]{1}@",
                               "[0-9]{7,9}@",
                               "[A-Z]{1}@",
                               "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                               "[0-9]{2}[/][0-9]{2}[/][0-9]{4}"))

    """
    Se presenta el caso de la falta del DNI y (parcial) del apellido al comenzar la lectura, para ciertas lecturas. 
    Por eso se mantiene una versión 'soft' de la expresión regular

    Muestra 'soft' de DNI tarjeta generación 1 con teclado US:

        INA"NOELIA SOLANGE"F"30782570"D"16/04/1984"26/11/2018"273

    Muestra 'soft' de DNI tarjeta generación 2 con teclado ES:

        INA@NOELIA SOLANGE@F@30782570@D@16/04/1984@26/11/2018@273

    """

    dni_gen_tres_soft_us = "".join(("[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                                    "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                                    "[A-Z]{1}\"",
                                    "[0-9]{7,9}\"",
                                    "[A-Z]{1}\"",
                                    "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                                    "[0-9]{2}[-][0-9]{2}[-][0-9]{4}"))

    dni_gen_tres_soft_es = "".join(("[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                                    "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                                    "[A-Z]{1}@",
                                    "[0-9]{7,9}@",
                                    "[A-Z]{1}@",
                                    "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                                    "[0-9]{2}[/][0-9]{2}[/][0-9]{4}"))

    """
    Muestra de DNI tarjeta generación 2 con teclado US:

        "14808837    "A"1"GALETTO"SUSANA BEATRIZ"ARGENTINA"24-02-1962"F"18-07-2011"00059458832"8212"18-07-2026"42"0"ILRÑ2.01 CÑ110613.02 )No Cap.="UNIDAD ·19 ÇÇ S-NÑ 0040:2008::00__

    Existen casos donde se agrega un campo desconocido al inicio de la cadena. El mismo es desestimado, pero cuenta a la hora de contar la cantidad de elementos cuando se parte la cadena por el separador de campos.

        2"14808837    "A"1"GALETTO"SUSANA BEATRIZ"ARGENTINA"24-02-1962"F"18-07-2011"00059458832"8212"18-07-2026"42"0"ILRÑ2.01 CÑ110613.02 )No Cap.="UNIDAD ·19 ÇÇ S-NÑ 0040:2008::00__

    Muestra de DNI tarjeta generación 2 con teclado ES:

        @11793518    @A@1@NIEVA@ANA MARIA@ARGENTINA@01/11/1955@F@05/11/2010@00025969635@2128 @05/11/2025@602@0@ILR:01.2 C:100817.01@UNIDAD #07 || S/N: 0040>2008>>0002

    """
    dni_gen_dos_us = "".join(("^(:?(.*)\"|\")[0-9]{0,}(.*)\"",
                              "[A-Z]{1}\"",
                              "[0-9]{1}\"",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}\"",
                              "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                              "[A-Z]{1}\"",
                              "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                              "[0-9]{10,}\"",
                              "[0-9]{4,}[\s]{0,}\"",
                              "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                              "[0-9]{1,}\"",
                              "(.*)"))

    dni_gen_dos_es = "".join(("^(:?(.*)\@|\@)[0-9]{0,}(.*)@",
                              "[A-Z]{1}@",
                              "[0-9]{1}\@",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}@",
                              "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                              "[A-Z]{1}@",
                              "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                              "[0-9]{10,}@",
                              "[0-9]{4,}[\s]{0,}@",
                              "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                              "[0-9]{1,}@",
                              "(.*)"))
    """
    Muestra de DNI tarjeta generación 1 con teclado US:

        "25307226    "A"1"VIVAS"ELIANA GUILLERMINA"ARGENTINA"07/04/1976"F"07/04/2010"00007595709"2128"1490"ILR:01.11 C:100328.01"UNIDAD ·12 || S/N: 0040>2008>>0014

    Muestra de DNI tarjeta generación 2 con teclado ES:

        @25307226    @A@1@VIVAS@ELIANA GUILLERMINA@ARGENTINA@07/04/1976@F@07/04/2010@00007595709@2128@1490@ILR:01.11 C:100328.01@UNIDAD ·12 || S/N: 0040>2008>>0014

    """
    dni_gen_uno_us = "".join(("^(:?(.*)\"|\")[0-9]{0,}(.*)\"",
                              "[A-Z]{1}\"",
                              "[0-9]{1}\"",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}\"",
                              "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                              "[A-Z]{1}\"",
                              "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                              "[0-9]{10,}\"",
                              "[0-9]{4,}\"",
                              "[0-9]{4,}\"",
                              "(.*)"))

    dni_gen_uno_es = "".join(("^(:?(.*)\@|\@)[0-9]{0,}(.*)@",
                              "[A-Z]{1}@",
                              "[0-9]{1}\@",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                              "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}@",
                              "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                              "[A-Z]{1}@",
                              "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                              "[0-9]{10,}@",
                              "[0-9]{4,}@",
                              "[0-9]{4,}@",
                              "(.*)"))
    """
    Se presenta el caso de la falta del DNI al comenzar la lectura, para ciertas lecturas. Por eso se mantiene una versión 'soft' de la expresión regular

    Muestra 'soft' de DNI tarjeta generación 1 con teclado US:

        "A"1"VIVAS"ELIANA GUILLERMINA"ARGENTINA"07/04/1976"F"07/04/2010"00007595709"2128"1490"ILR:01.11 C:100328.01"UNIDAD ·12 || S/N: 0040>2008>>0014

    Muestra 'soft' de DNI tarjeta generación 2 con teclado ES:

        @A@1@VIVAS@ELIANA GUILLERMINA@ARGENTINA@07/04/1976@F@07/04/2010@00007595709@2128@1490@ILR:01.11 C:100328.01@UNIDAD ·12 || S/N: 0040>2008>>0014

    """
    dni_gen_uno_soft_us = "".join(("^(:?(.*)\"|\")[A-Z]{1}\"",
                                   "[0-9]{1}\"",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}\"",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}\"",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                                   "[A-Z]{1}\"",
                                   "[0-9]{2}[-][0-9]{2}[-][0-9]{4}\"",
                                   "[0-9]{10,}\"",
                                   "[0-9]{4,}\"",
                                   "[0-9]{4,}\"",
                                   "(.*)"))

    dni_gen_uno_soft_es = "".join(("^(:?(.*)\@|\@)[A-Z]{1}@",
                                   "[0-9]{1}\@",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}([\s][A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}){0,}@",
                                   "[A-Za-zÁÉÍÓÚÜñáéíóúüÑ\']{1,}@",
                                   "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                                   "[A-Z]{1}@",
                                   "[0-9]{2}[/][0-9]{2}[/][0-9]{4}@",
                                   "[0-9]{10,}@",
                                   "[0-9]{4,}@",
                                   "[0-9]{4,}@",
                                   "(.*)"))

    def __init__(self, input_string):
        # Es necesario reemplazar los espacios múltiples por espacios simples
        input_string = sub("\s+", ' ', input_string)
        self.teclado = None
        self.tipo_documento = None
        self.muestra = input_string.strip()
        if search(self.carnet_conductor_us, self.muestra) and len(self.muestra.split("\n")) == 19:
            self.teclado = "US"
            self.tipo_documento = TipoDocumento.CONDUCTOR
            values = self.muestra.split("\n")
            self.dni = values[1]
            self.sexo = values[2]
            self.nombres = values[3]
            self.apellidos = values[4]
            self.fecha_nacimiento = values[5]
            self.pais = values[6]
            self.direccion_calle = values[7]
            self.direccion_numero = values[8]
            self.direccion_piso = values[9]
            self.direccion_depto = values[10]
            self.direccion_barrio = values[11]
            self.ciudad = values[12]
            self.codigo_postal = values[13]
            self.fecha_emision_documento = values[14]
            self.fecha_vencimiento_documento = values[15]
            self.carnet_conductor_categoria = values[16]
            self.grupo_factor_sanguineo = values[17]
            self.numero_tramite = values[18]
        elif search(self.carnet_conductor_es, self.muestra) and len(self.muestra.split("\n")) == 19:
            self.teclado = "ES"
            self.tipo_documento = TipoDocumento.CONDUCTOR
            values = self.muestra.split("\n")
            self.dni = values[1]
            self.sexo = values[2]
            self.nombres = values[3]
            self.apellidos = values[4]
            self.fecha_nacimiento = values[5]
            self.pais = values[6]
            self.direccion_calle = values[7]
            self.direccion_numero = values[8]
            self.direccion_piso = values[9]
            self.direccion_depto = values[10]
            self.direccion_barrio = values[11]
            self.ciudad = values[12]
            self.codigo_postal = values[13]
            self.fecha_emision_documento = values[14]
            self.fecha_vencimiento_documento = values[15]
            self.carnet_conductor_categoria = values[16]
            self.grupo_factor_sanguineo = values[17]
            self.numero_tramite = values[18]
        elif search(self.dni_gen_tres_us, self.muestra) and len(self.muestra.split("\"")) >= 8:
            self.teclado = "US"
            self.tipo_documento = TipoDocumento.DNI_GEN_3
            values = self.muestra.split("\"")
            self.numero_tramite = values[0]
            self.apellidos = values[1]
            self.nombres = values[2]
            self.sexo = values[3]
            self.dni = values[4]
            self.ejemplar = values[5]
            self.fecha_nacimiento = values[6]
            self.fecha_emision_documento = values[7]
        elif search(self.dni_gen_tres_es, self.muestra) and len(self.muestra.split("@")) >= 8:
            self.teclado = "ES"
            self.tipo_documento = TipoDocumento.DNI_GEN_3
            values = self.muestra.split("@")
            self.numero_tramite = values[0]
            self.apellidos = values[1]
            self.nombres = values[2]
            self.sexo = values[3]
            self.dni = values[4]
            self.ejemplar = values[5]
            self.fecha_nacimiento = values[6]
            self.fecha_emision_documento = values[7]
        elif search(self.dni_gen_tres_soft_us, self.muestra) and len(self.muestra.split("\"")) >= 8:
            self.teclado = "US"
            self.tipo_documento = TipoDocumento.DNI_GEN_3
            values = self.muestra.split("\"")
            self.ejemplar = None
            self.apellidos = None
            self.nombres = values[1]
            self.sexo = values[2]
            self.dni = values[3]
            self.ejemplar = values[4]
            self.fecha_nacimiento = values[5]
            self.fecha_emision_documento = values[6]
            self.fecha_emision_documento = values[7]
        elif search(self.dni_gen_tres_soft_es, self.muestra) and len(self.muestra.split("@")) >= 8:
            self.teclado = "ES"
            self.tipo_documento = TipoDocumento.DNI_GEN_3
            values = self.muestra.split("@")
            self.ejemplar = None
            self.apellidos = None
            self.nombres = values[1]
            self.sexo = values[2]
            self.dni = values[3]
            self.ejemplar = values[4]
            self.fecha_nacimiento = values[5]
            self.fecha_emision_documento = values[6]
        elif search(self.dni_gen_dos_us, self.muestra) and len(self.muestra.split("\"")) >= 17:
            self.teclado = "US"
            self.tipo_documento = TipoDocumento.DNI_GEN_2
            values = self.muestra.split("\"")
            self.dni = values[1].strip()
            self.ejemplar = values[2]
            self.apellidos = values[4]
            self.nombres = values[5]
            self.pais = values[6]
            self.fecha_nacimiento = values[7]
            self.sexo = values[8]
            self.fecha_emision_documento = values[9]
            self.numero_tramite = values[10]
            self.of_ident = values[11]
            self.fecha_vencimiento_documento = values[12]
        elif search(self.dni_gen_dos_es, self.muestra) and len(self.muestra.split("@")) >= 17:
            self.teclado = "ES"
            self.tipo_documento = TipoDocumento.DNI_GEN_2
            values = self.muestra.split("@")
            self.dni = values[1].strip()
            self.ejemplar = values[2]
            self.apellidos = values[4]
            self.nombres = values[5]
            self.pais = values[6]
            self.fecha_nacimiento = values[7]
            self.sexo = values[8]
            self.fecha_emision_documento = values[9]
            self.numero_tramite = values[10]
            self.of_ident = values[11]
            self.fecha_vencimiento_documento = values[12]
        elif search(self.dni_gen_uno_us, self.muestra) and len(self.muestra.split("\"")) >= 15:
            self.teclado = "US"
            self.tipo_documento = TipoDocumento.DNI_GEN_1
            values = self.muestra.split("\"")
            self.dni = values[1].strip()
            self.ejemplar = values[2]
            self.apellidos = values[4]
            self.nombres = values[5]
            self.pais = values[6]
            self.fecha_nacimiento = values[7]
            self.sexo = values[8]
            self.fecha_emision_documento = values[9]
            self.numero_tramite = values[10]
            self.of_ident = values[11]
        elif search(self.dni_gen_uno_es, self.muestra) and len(self.muestra.split("@")) >= 15:
            self.teclado = "ES"
            self.tipo_documento = TipoDocumento.DNI_GEN_1
            values = self.muestra.split("@")
            self.dni = values[1].strip()
            self.ejemplar = values[2]
            self.apellidos = values[4]
            self.nombres = values[5]
            self.pais = values[6]
            self.fecha_nacimiento = values[7]
            self.sexo = values[8]
            self.fecha_emision_documento = values[9]
            self.numero_tramite = values[10]
            self.of_ident = values[11]
        elif search(self.dni_gen_uno_soft_us, self.muestra) and len(self.muestra.split("\"")) >= 14:
            self.teclado = "US"
            self.tipo_documento = TipoDocumento.DNI_GEN_1
            values = self.muestra.split("\"")
            # Establecido DNI específicamente a None, ya que es un valor de consulta recurrente
            self.dni = None
            self.ejemplar = values[1]
            self.apellidos = values[3]
            self.nombres = values[4]
            self.pais = values[5]
            self.fecha_nacimiento = values[6]
            self.sexo = values[7]
            self.fecha_emision_documento = values[8]
            self.numero_tramite = values[9]
            self.of_ident = values[10]
        elif search(self.dni_gen_uno_soft_es, self.muestra) and len(self.muestra.split("@")) >= 14:
            self.teclado = "ES"
            self.tipo_documento = TipoDocumento.DNI_GEN_1
            values = self.muestra.split("@")
            self.dni = None
            self.ejemplar = values[1]
            self.apellidos = values[3]
            self.nombres = values[4]
            self.pais = values[5]
            self.fecha_nacimiento = values[6]
            self.sexo = values[7]
            self.fecha_emision_documento = values[8]
            self.numero_tramite = values[9]
            self.of_ident = values[10]

    def __str__(self):
        return "\n".join(("Nombre: " + self.nombres,
                          "Apellido: " + (self.apellidos if self.apellidos else "-"),
                          "Documento: " + (self.dni if self.dni else "-"),
                          "Fecha nacimiento: " + self.fecha_nacimiento,
                          "Sexo: " + self.sexo,
                          "Tipo documento: " + self.tipo_documento.value))
