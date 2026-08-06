DONE:

1. (escasamente importante) bsw (prosper: pruebas directamente de la bsae de datos para el bsw que el user escoja la prueba que quiera usar) - Además de los pozos , que escoja la prueba que queire utilizar para el bsw.
        - escoger prueba (1, 2, 3, ...)
        - promedio de pruebas
2. (critica alta) interfaz manual: poder ingresar el bsw manualmente, tanto en la interfaz como en el csv (cajas). 

3. agregar wct a manual input. (D)**
4. descargar informe en pdf.** 
5. kpi para optimizacion global (punto óptimo máximo). (B)**
6. kpi con diferencia de gas para alcanzar la produccion máxima (constrained) - generalizacion del kpi actual. (C)**
7. leer de la base de datos las ultimas pruebas para graficar y compara con la optimización
8. tarea pendiente: generar un script propio para el contenido de results_of_optimization (SiS)

TODO:
1. En el histporico agregar colores a las pruebas para distinguir su fecha de realización.
2. Mirar lo de los procesos gaussianos para sacar curvas de performances (priors) del historico de pruebas.
3. Incluir en el modelo e optimización el bsw en función del qgl para pesar la curva de aceite. 
4. incluir un slider para mirar una ventana de pruebas del histórico (con color para fechas). 
5. tarea pendiente: generar un script propio para el contenido de results_of_optimization (snowpark container)
6. llm para generar un analisis automático de la optimización. 
7. agregar slider en optimización global.

7. modifcar la interfaz de carga (nombre de la planta, selección de pozos (prosper)) para evitar los posibles erroes de formato en el csv. 
8. (baja) tabla en base de datos para información de optimizacion global. 
9. agregar MRP a optimizacion global (OK con clonclusion: no depende del MPR)
10. (criticidad baja) modelo mrp opcional actibable/desactivable. fisico y económico (usar varios pozos de los datos ya disponibles). 
11. convertir proper a clases._
12. Añadir intervalos de confianza para la producción.


UNKOWN:
1. arreglar lo del la lista de well restuls para optimizaciones anterioes en el historal (tab 3) (A)**
2. (critica medio) aceptar n pozos en el csv. tomar el número de columnas y dividir por 2. 
3. (medio) procentaje de fidelidad en función de los puntos o medidas. 



ideas:
- Entregar analisis de datos en el reporte dinámico.
- Usar sistema ATS para la carga de datos.

- (actualización tab2) visualizar las pruebas y trazar las curvas de performance (incluyendo en color la fecha). parametro: rango de fechas y ver los datos de los diferentes pozos.  

- it is not necessart to call the database to get the well optimization results
DisplayConstrainedResults just requires the optimization results (just one parameter)