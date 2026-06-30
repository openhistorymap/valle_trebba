Valle Trebba — pacchetto cartografia + modello 3D
==================================================

Bounding box geografico (EPSG:4326), derivato dai 1222 punti tombe della
necropoli con buffer di 2000 m:
  W = 12.08247890   S = 44.68059874
  E = 12.14198675   N = 44.73302268
Territorio: 4.7159 km (E-W) x 5.8257 km (N-S),  aspect = 0.8095.

----------------------------------------------------------------------
Contenuto
----------------------------------------------------------------------

1) IMMAGINI (4047 x 5000 px, ~1.17 m/px)

   valle-trebba-wms-agea2011.jpg
       Ortofoto pura AGEA 2011 RGB della Regione Emilia-Romagna,
       servita via WMS dal portale `servizigis.regione.emilia-romagna.it`.
       Niente overlay sopra.

   valle-trebba-5.png
       Stesso bbox, render completo: WMS sotto + livello "Sfondo"
       verde-grigio sabbia paludosa + overlay archeologici
       (linea-di-costa, paleoalvei, cordoni, dossi, valle-pega-dossi,
       ustrina, passerelle, abitato). I dossi sono in primo piano in
       tinta sabbia calda.

2) MODELLO 3D (piano piatto, geometria identica tra le due varianti)

   valle-trebba-wms-agea2011.obj + .mtl
       Quad piatto su Z=0 con texture l'ortofoto pura.

   valle-trebba-5.obj + .mtl
       Stessa geometria, texture il render completo.

   Sistema di coordinate del piano:
     - Origine 0,0,0 nell'angolo SW (sud-ovest).
     - +X = est,  +Y = nord,  +Z = up.
     - Unita': kilometri (1 unit = 1 km).
     - Dimensioni: 4.7159 x 5.8257 km.

   Apribile in Blender, MeshLab, three.js (OBJLoader+MTLLoader): tenere
   .obj, .mtl e .jpg/.png nella stessa cartella.

3) DATI

   valle_trebba_tombe_obj_local.json
       1222 punti tombe della necropoli, gia' proiettati nelle
       coordinate locali dell'OBJ (in km). Ogni feature ha:
         geometry.coordinates = [x_km, y_km, 0.0]
         properties.<originali> + _lon, _lat per round-trip.
       Header con bbox geografico, trasformazione esatta, e indicazione
       dell'OBJ di riferimento.
       Estensione .json (non .geojson) perche' RFC 7946 vincola GeoJSON
       a WGS84: queste sono coord locali cartesiane.

   valle_trebba.bbox.json
       Bbox geografico + dimensioni immagine + dimensioni territorio km.

----------------------------------------------------------------------
Trasformazione lon/lat <-> coord OBJ
----------------------------------------------------------------------

   x_km = (lon - W) / (E - W) * 4.7159
   y_km = (lat - S) / (N - S) * 5.8257
   z    = 0
