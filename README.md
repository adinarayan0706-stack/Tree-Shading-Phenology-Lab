# Tree Shading & Phenology Lab

Hey! This is a complete project I put together for calculating and visualizing how trees cast shadows and shed their leaves throughout the year. If you have ever tried to figure out how much ground area a tree actually shades at different times of the day, or how deciduous trees drop their leaves in the spring while evergreens keep going, this tool maps it all out in 3D and 2D.

It handles all 9 required tree species: Mango, Banana, Amla, Sheesham, Sagvan (Teak), Kathal (Jackfruit), Jamun, Ber, and Papaya.

### What It Does & How It Works

The whole project runs out of a single Python server that serves up an interactive web dashboard. When you open it up, you get a 3D viewport rendered with Three.js where you can check out the tree. You can click and drag left across the screen to spin the tree 360 degrees on its turntable pedestal just like inspecting a character in a lobby, right-click to orbit around it, and scroll to zoom in and out.

On the left side panel, you have a full suite of sliders. You can scale the tree from a tiny sapling up to full maturity, adjust its canopy spread multiplier, and tweak the leaf foliage cover and wind speed for falling leaf animations. There are also controls for changing the time of day, scrubbing through all 365 days of the year, and adjusting your latitude. If you don't want to drag the day slider manually, there are quick preset buttons for seasons like spring, summer, the summer solstice, monsoon, autumn, winter, and the new year.

As you move the sliders around, the mathematical engine computes everything in real time. It uses Cooper's Equation to track solar declination based on the day of the year, combines that with your latitude and the hour angle to find the exact solar elevation angle, and calculates the shadow length cast on flat ground. It also factors in annual phenology cycles—meaning deciduous trees like Sagvan and Sheesham will visibly drop their leaves down to bare branches during their dry seasons while falling leaves flutter down to the ground, and evergreens like Mango or Kathal maintain dense continuous canopies.

Over on the right-hand panel, there are live 2D analytical diagrams that update instantly. These include a side-profile shadow triangle showing height and shadow length, a top-down compass footprint map, a diurnal hourly curve showing how shaded area changes from morning to evening, an annual phenology plot tracking leaf coverage across 365 days, and a live bar chart comparing the effective shaded area across all 9 species.

There is also a "Project Notes & All Calculations" button at the top of the control panel that opens up a full worked math sheet with step-by-step formulas and a complete comparison table for all 9 species, which makes it super handy for presentations or viva walkthroughs. Plus, there is a CSV export button if you ever need to dump your simulation data into a spreadsheet.

### How to Run It

You don't need any heavy configuration or complex node module installations—just standard Python 3.

1. Clone or download this repository onto your computer:
```bash
git clone https://github.com/adinarayan0706-stack/Tree-Shading-Phenology-Lab.git
cd Tree-Shading-Phenology-Lab

```


2. Fire up the application by running the main Python script:
```bash
python3 app.py

```


3. The script will automatically start a local HTTP server on your machine and open up your default web browser directly to `[http://127.0.0.1:5000](http://127.0.0.1:5000)`.

### The Math Behind It

The core calculations implemented in the backend and frontend engine rely on standard arboricultural and solar geometry equations:

1. **Solar Declination (Cooper's Equation):**

$$\delta = 23.45^\circ \times \sin\left(\frac{360}{365} \times (284 + N)\right)$$



*(where $N$ is the sequential day of the year).*
2. **Solar Elevation Angle:**

$$\sin(\theta) = \sin(\phi)\sin(\delta) + \cos(\phi)\cos(\delta)\cos(\omega)$$



*(where $\phi$ is your latitude and $\omega$ is the hour angle based on local solar time).*
3. **Shadow Length:**

$$L = \frac{H(t)}{\tan(\theta)}$$



*(where $H(t)$ is the current biometric height of the tree at a given growth percentage).*
4. **Effective Shaded Land Area:**

$$A_{eff} = \pi \times \left(R + \frac{L}{2}\right) \times R \times \eta_{leaf}(N)$$



*(where $R$ is the crown radius and $\eta_{leaf}(N)$ is the live seasonal leaf density factor).*

### Project Structure

```text
Tree-Shading-Phenology-Lab/
├── app.py             # Python server and mathematical calculation engine
├── templates/
│   └── index.html     # Frontend code (Three.js viewport, UI controls, and 2D charts)
├── README.md          # Project documentation
└── LICENSE            # MIT License

```

### License

This project is open-source and available under the terms of the [MIT License](https://www.google.com/search?q=LICENSE).
