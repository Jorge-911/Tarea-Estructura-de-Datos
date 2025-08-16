# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Inventarios (archivo único, comentarios detallados)

Objetivo del programa
---------------------
Implementar un inventario simple que permita:
  - Añadir productos
  - Eliminar productos por ID
  - Actualizar cantidad o precio por ID
  - Buscar productos por nombre (coincidencia parcial, nombres similares)
  - Listar todos los productos
…mediante un menú de consola.

Decisiones de diseño (por qué así y no de otra forma)
-----------------------------------------------------
1) Estructura de datos principal = LISTA en la clase Inventario
   - El enunciado pide explícitamente “una lista de productos”.
   - Implica búsquedas lineales O(n). Es aceptable para ejercicios académicos o inventarios pequeños/medios.
   - Si el volumen creciera, sería ideal migrar a un diccionario {id: producto} para O(1) promedio por ID,
     pero aquí priorizamos cumplir el requisito de “lista”.

2) Unicidad de ID
   - Antes de agregar, se recorre la lista para comprobar que no exista ese ID (validación O(n)).
   - Se asume que el ID lo define el usuario (no se auto-genera). Si se repite, se rechaza el alta.

3) Clase Producto con getters y setters
   - Python permite acceder directamente a atributos o usar @property.
   - Implementamos getters/setters explícitos porque el enunciado lo solicita.
   - Los setters centralizan validaciones (no negativos, nombre no vacío, números válidos).

4) Búsqueda por nombre (nombres “similares”)
   - Coincidencia por subcadena e insensible a mayúsculas/minúsculas (case-insensitive).
   - Retorna una lista de coincidencias (posiblemente vacía).

5) Interfaz de consola robusta
   - Menú simple, claro y cíclico.
   - Lectura segura de números: floats aceptan coma decimal (“1,25”) convirtiéndola a punto (“1.25”).
   - Manejo de errores controlado: entradas inválidas muestran mensajes amigables y no rompen el programa.

Supuestos hechos (para acotar el problema)
------------------------------------------
- No hay persistencia: al cerrar el programa, se pierde el inventario (se podría añadir JSON/CSV/SQLite).
- Precio en USD y puede tener decimales.
- Cantidad es un entero ≥ 0.
- ID y nombre no pueden ser vacíos.
"""

from typing import List, Optional


class Producto:
    """
    Representa un producto del inventario.

    Atributos:
      - id (str): identificador único NO vacío.
      - nombre (str): nombre NO vacío.
      - cantidad (int): unidades en stock, entero ≥ 0.
      - precio (float): precio unitario, número ≥ 0.

    Por qué getters/setters:
      - El enunciado lo requiere. Además, permiten validar y normalizar cuando se actualiza.
    """

    def __init__(self, id_: str, nombre: str, cantidad: int, precio: float):
        # Guardamos “protegido” con _ prefijo para forzar el uso de getters/setters si hiciera falta.
        self._id = str(id_).strip()          # Normalizamos espacios
        self._nombre = str(nombre).strip()

        # Convertimos y validamos cantidad como entero no negativo
        try:
            self._cantidad = int(cantidad)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un entero.")
        if self._cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")

        # Precio: aceptamos coma decimal por comodidad de entrada
        try:
            self._precio = float(str(precio).replace(",", "."))
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número.")
        if self._precio < 0:
            raise ValueError("El precio no puede ser negativo.")

        # Validaciones de campos de texto
        if not self._id:
            raise ValueError("El ID no puede estar vacío.")
        if not self._nombre:
            raise ValueError("El nombre no puede estar vacío.")

    # --- Getters (cumplen requisito) ---
    def get_id(self) -> str:
        """Retorna el ID único del producto."""
        return self._id

    def get_nombre(self) -> str:
        """Retorna el nombre del producto."""
        return self._nombre

    def get_cantidad(self) -> int:
        """Retorna la cantidad disponible en inventario."""
        return self._cantidad

    def get_precio(self) -> float:
        """Retorna el precio unitario del producto."""
        return self._precio

    # --- Setters con validaciones (cumplen requisito) ---
    def set_nombre(self, nuevo_nombre: str) -> None:
        """
        Actualiza el nombre del producto. No se permite dejarlo vacío.
        Útil para correcciones de nombre o estandarizaciones.
        """
        nuevo_nombre = str(nuevo_nombre).strip()
        if not nuevo_nombre:
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = nuevo_nombre

    def set_cantidad(self, nueva_cantidad: int) -> None:
        """
        Actualiza la cantidad en stock. Debe ser entero y no negativo.
        """
        try:
            nueva_cantidad = int(nueva_cantidad)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un entero.")
        if nueva_cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        self._cantidad = nueva_cantidad

    def set_precio(self, nuevo_precio: float) -> None:
        """
        Actualiza el precio unitario. Debe ser número y no negativo.
        Se admite coma decimal para facilitar la digitación.
        """
        try:
            nuevo_precio = float(str(nuevo_precio).replace(",", "."))
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número.")
        if nuevo_precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = nuevo_precio

    def __str__(self) -> str:
        """
        Representación legible del producto para listados y resultados de búsqueda.
        """
        return f"ID: {self._id} | Nombre: {self._nombre} | Cant.: {self._cantidad} | Precio: ${self._precio:,.2f}"


class Inventario:
    """
    Gestiona una colección de productos usando una LISTA (requisito).

    Por qué lista:
      - Es lo solicitado. Aceptamos el costo de búsquedas O(n) por simplicidad.
      - Con poca/mediana cantidad de productos, el rendimiento es suficiente.

    Métodos:
      - agregar_producto(producto): valida ID único antes de añadir.
      - eliminar_por_id(id): elimina si existe y devuelve True/False.
      - actualizar(id, cantidad?, precio?): modifica cantidad y/o precio si existe.
      - buscar_por_nombre(termino): subcadena insensible a mayúsculas.
      - mostrar_todos(): devuelve una copia de la lista.
    """

    def __init__(self):
        # Lista principal de productos
        self.productos: List[Producto] = []

    def agregar_producto(self, producto: Producto) -> None:
        """
        Añade un producto, asegurando que el ID sea único.
        Implementación: búsqueda lineal para detectar colisión de ID.
        """
        if self._existe_id(producto.get_id()):
            raise ValueError(f"Ya existe un producto con ID '{producto.get_id()}'.")
        self.productos.append(producto)

    def eliminar_por_id(self, id_producto: str) -> bool:
        """
        Elimina el producto con el ID indicado. Retorna True si se eliminó, False si no se encontró.
        Implementación: iteramos con índice para poder usar 'del' y borrar in-place.
        """
        id_producto = str(id_producto).strip()
        for i, p in enumerate(self.productos):
            if p.get_id() == id_producto:
                del self.productos[i]
                return True
        return False

    def actualizar(self, id_producto: str,
                   cantidad: Optional[int] = None,
                   precio: Optional[float] = None) -> bool:
        """
        Actualiza cantidad y/o precio del producto con el ID indicado.
        - Si cantidad o precio son None, ese campo no se modifica.
        - Usa los setters del producto (heredando sus validaciones).
        """
        prod = self._buscar_por_id(id_producto)
        if not prod:
            return False
        if cantidad is not None:
            prod.set_cantidad(cantidad)
        if precio is not None:
            prod.set_precio(precio)
        return True

    def buscar_por_nombre(self, termino: str) -> List[Producto]:
        """
        Retorna una lista de productos cuyo nombre contiene 'termino' (subcadena),
        sin distinguir mayúsculas/minúsculas (case-insensitive).
        """
        termino = str(termino).strip().lower()
        if not termino:
            return []  # Si no hay término, no devolver todo: evita “falsos positivos”.
        return [p for p in self.productos if termino in p.get_nombre().lower()]

    def mostrar_todos(self) -> List[Producto]:
        """
        Devuelve una copia superficial de la lista de productos.
        Decisión: no exponemos la lista interna para evitar modificaciones no controladas.
        """
        return list(self.productos)

    # -------- Auxiliares internos --------
    def _existe_id(self, id_producto: str) -> bool:
        """True si ya hay un producto con ese ID (búsqueda lineal)."""
        return any(p.get_id() == id_producto for p in self.productos)

    def _buscar_por_id(self, id_producto: str) -> Optional[Producto]:
        """Devuelve el producto con ese ID o None si no existe."""
        id_producto = str(id_producto).strip()
        for p in self.productos:
            if p.get_id() == id_producto:
                return p
        return None


# ============================
# Interfaz de Usuario (Consola)
# ============================

def _mostrar_menu():
    """
    Presenta el menú principal. Las opciones cubren todos los requisitos del enunciado.
    """
    print("""
========== MENÚ INVENTARIO ==========
1) Añadir producto
2) Eliminar producto por ID
3) Actualizar cantidad o precio por ID
4) Buscar producto(s) por nombre
5) Mostrar todos los productos
6) Salir
=====================================
""")


def _pedir_float(msg: str) -> float:
    """
    Lee un float del usuario, aceptando coma decimal.
    Se repite hasta obtener un valor válido, evitando que el programa se caiga.
    """
    while True:
        try:
            return float(input(msg).replace(",", "."))
        except ValueError:
            print("Entrada inválida. Intente de nuevo.")


def _pedir_int(msg: str) -> int:
    """
    Lee un entero del usuario. Reintenta hasta que sea válido.
    """
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Entrada inválida. Intente de nuevo.")


def main():
    """
    Bucle principal del programa (CLI):
      - Crea un Inventario vacío (no persistente).
      - Muestra menú y procesa la opción elegida.
      - Maneja errores de validación mostrando mensajes claros.
    """
    inventario = Inventario()

    # Datos de ejemplo (descomentar si se quiere iniciar con algo):
    # inventario.agregar_producto(Producto("A001", "Agua 600ml", 20, 0.6))
    # inventario.agregar_producto(Producto("B010", "Batería AA", 50, 1.2))

    while True:
        _mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            # --- Añadir producto ---
            print("-- Añadir nuevo producto --")
            idp = input("ID: ").strip()
            nombre = input("Nombre: ").strip()
            cantidad = _pedir_int("Cantidad: ")
            precio = _pedir_float("Precio (USD): ")
            try:
                prod = Producto(idp, nombre, cantidad, precio)
                inventario.agregar_producto(prod)
                print("Producto agregado correctamente.\n")
            except Exception as e:
                # Captura validaciones (ID/nombre vacíos, repetido, cantidad/precio inválidos)
                print(f"Error: {e}\n")

        elif opcion == "2":
            # --- Eliminar por ID ---
            print("-- Eliminar producto --")
            idp = input("ID del producto a eliminar: ").strip()
            if inventario.eliminar_por_id(idp):
                print("Producto eliminado.\n")
            else:
                print("No se encontró un producto con ese ID.\n")

        elif opcion == "3":
            # --- Actualizar (cantidad y/o precio) ---
            print("-- Actualizar producto --")
            idp = input("ID del producto a actualizar: ").strip()
            print("Deje vacío si NO desea cambiar ese campo.")
            cant_str = input("Nueva cantidad: ").strip()
            prec_str = input("Nuevo precio (USD): ").strip()

            # Conversión dentro de try para capturar errores de entrada (p. ej., “abc”)
            try:
                cantidad = None
                precio = None

                if cant_str != "":
                    cantidad = int(cant_str)  # puede lanzar ValueError
                if prec_str != "":
                    precio = float(prec_str.replace(",", "."))  # puede lanzar ValueError

                if inventario.actualizar(idp, cantidad=cantidad, precio=precio):
                    print("Producto actualizado.\n")
                else:
                    print("No se encontró un producto con ese ID.\n")

            except ValueError as e:
                # Mensajes claros para entradas no numéricas o inválidas
                print(f"Error: {e}\n")
            except Exception as e:
                print(f"Error inesperado: {e}\n")

        elif opcion == "4":
            # --- Buscar por nombre ---
            print("-- Buscar productos --")
            termino = input("Buscar por nombre: ").strip()
            resultados = inventario.buscar_por_nombre(termino)
            if resultados:
                print("Resultados:")
                for p in resultados:
                    print("  ", p)
            else:
                print("No se encontraron productos que coincidan.")
            print()

        elif opcion == "5":
            # --- Listar todos ---
            print("-- Inventario actual --")
            productos = inventario.mostrar_todos()
            if not productos:
                print("(vacío)\n")
            else:
                for p in productos:
                    print("  ", p)
                print()

        elif opcion == "6":
            # --- Salir ---
            print("Saliendo... ¡Hasta luego!")
            break

        else:
            print("Opción inválida. Intente nuevamente.\n")


# Punto de entrada del script
if __name__ == "__main__":
    main()

"""
Ideas de extensión (no implementadas para cumplir el alcance):
- Persistencia: guardar/cargar en JSON/CSV/SQLite para no perder datos al cerrar.
- Reportes: valor total de inventario, alertas de stock bajo, etc.
- Validaciones extra: longitudes máximas, formatos de ID, catálogos de categorías.
- Arquitectura por capas o API REST si se desea crecer más allá de consola.
"""
