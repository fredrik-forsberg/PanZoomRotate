# PanZoomRotate

1. [Svenska &#127480;&#127466;](#1-svenska-)

    1.1. [Generell information](#11-generell-information)

    1.2. [Användning](#12-användning)

    1.3. [Funktioner](#13-funktioner)

2. [English &#127468;&#127463;](#2-english-)

    2.1. [General information](#21-general-information)

    2.2. [Setup](#22-setup)

    2.3. [Features](#23-features)

<br/>
<br/>

## 1. Svenska &#127480;&#127466;

### 1.1. Generell information
Banläggningsprogram för orientering (som OCAD och PurplePen) saknar stöd för rotation av kartan, något som behövs för att kunna bedöma olika vägval. PanZoomRotate skrevs för att lösa det problemet, men kan givetvis användas i andra sammanhang där en bildfil eller själva bildskärmen behöver panoreras, zoomas och/eller roteras.
<br/>

### 1.2. Användning
Det finns två sätt att komma igång med PanZoomRotate:
* **Enklaste sättet - Med EXE-fil:**
    
    Om du använder en Windows-dator kan du helt enkelt ladda ner [PanZoomRotate.exe](../../raw/main/PanZoomRotate.exe) och dubbelklicka på filen när den har laddats ner klart, sedan är du igång!
    
    (EXE-filen genererades från Python-koden med hjälp av Python-paketet [PyInstaller](https://pypi.org/project/pyinstaller/))

    
* **Mer avancerat - Med Python:**
    
    Kör [PanZoomRotate.py](/PanZoomRotate.py) med Python 3. Följande paket måste vara installerade:
    * [numpy](https://pypi.org/project/numpy/)
    * [opencv-python](https://pypi.org/project/opencv-python/)
    * [Pillow](https://pypi.org/project/Pillow/)
    * [pynput](https://pypi.org/project/pynput/)
    * [PyMuPDF](https://pypi.org/project/PyMuPDF/)


### 1.3. Funktioner
* Panorera - Drag med vänster musknapp

* Zooma - Scrollhjulet eller "+"/"-"-tangenterna

* Rotera - Drag med höger musknapp
<br/>


* Global skärmdumpstangent - Förinställd som "§" (nedanför Escape) men kan ändras i menyn (se nedan)

* Öppna meny med alternativ - M, Alt-, eller Menytangenten
<br/>


* Fullskärm - F

* Återställ vy - R
<br/>


* Kopiera bild till Urklipp - Ctrl+C    (Om det stöds av operativsystemet)

* Klistra in bild från Urklipp - Ctrl+V

* Öppna bild- eller PDF-fil - Ctrl+O

* Spara bild - Ctrl+S


<br/>
***
<br/>

## 2. English &#127468;&#127463;

### 2.1. General information
[Orienteering](https://en.wikipedia.org/wiki/Orienteering) course setting software (such as OCAD and PurplePen) lack the option to rotate the map, a feature which is sorely missed while evaluating route choices. PanZoomRotate was written as a way of solving this problem, but it can of course be used in any situation where the screen itself or an image from a file needs to be panned, zoomed, and/or rotated.
<br/>

### 2.2. Setup
There are two ways to start using PanZoomRotate:
* **The easiest - Using EXE-file:**
    
    If you are using a Windows computer you can simply download [PanZoomRotate.exe](../../raw/main/PanZoomRotate.exe) and double click the file once the download is finished, then you are done!
    
    (The EXE-file was generated from the Python code using the Python package [PyInstaller](https://pypi.org/project/pyinstaller/))

    
* **More advanced - Using Python:**
    
    Run [PanZoomRotate.py](/PanZoomRotate.py) with Python 3. The following packages must be installed:
    * [numpy](https://pypi.org/project/numpy/)
    * [opencv-python](https://pypi.org/project/opencv-python/)
    * [Pillow](https://pypi.org/project/Pillow/)
    * [pynput](https://pypi.org/project/pynput/)
    * [PyMuPDF](https://pypi.org/project/PyMuPDF/)


### 2.3. Features
* Pan - Left click and drag

* Zoom - Scroll wheel or "+"/"-"-keys

* Rotate - Right click and drag
<br/>


* Global screenshot hotkey - Preset to "§" but can be changed in the menu during runtime (se below)

* Options menu - M, Alt-, or Menu-key
<br/>


* Fullscreen - F

* Reset view - R
<br/>


* Copy image to clipboard - Ctrl+C    (If supported by the system)

* Paste image from clipboard - Ctrl+V

* Open image or PDF - Ctrl+O

* Save image - Ctrl+S
