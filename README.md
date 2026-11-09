# Tree Shading & Phenology Lab

This is a web simulator I built for the problem statement given by Dr. Gagan Raj Gupta (IIT Bhilai). The goal is to calculate the land area shaded by a tree at different times of the day and year, while accounting for tree growth, leaf shedding, and falling leaves.

The dashboard lets you pick from 9 tree species. As you move the sliders for age, time of day, and day of the year, the 3D model and the 2D charts update in real time.

## How it works
The project runs on a simple Python HTTP server (`app.py`). The 3D tree is built using Three.js, and the 2D charts are drawn using the HTML5 Canvas API. All the simulation logic is handled in the `calc()` function in the JavaScript.

## The Math
I kept the math based on standard trigonometry and curve fitting. Here is a breakdown of the logic:

- Tree growth isn't linear. I used power curves so height grows fast initially and slows down, while the radius expands more gradually.
  Height = `m.h * Math.pow(ratio, 0.6)`
  Radius = `m.r * Math.pow(ratio, 1.4)`

- Sun elevation arcs across the sky. I used a sine wave for the daily motion and a cosine wave for the seasonal tilt.

- Shadow length uses basic right-triangle trigonometry. The tree is the vertical side, the shadow is the horizontal side.
  Shadow = `h / Math.tan(el * Math.PI / 180)`

- Shaded area assumes the canopy casts an elliptical shadow on the ground. I calculate the area of that ellipse and multiply it by the current leaf density.
  Area = `Math.PI * rad * (rad + sh / 2) * den`

- Leaf density uses a cosine wave centered on each tree's specific shedding peak (e.g., Mango sheds around day 75).

## How to run it
You only need Python 3 installed. No pip installs or node modules are required.

1. Clone the repo.
2. Run `python app.py`
3. It will automatically open http://localhost:8080 in your browser.

## Future Scope
The current solar model uses a simplified sine/cosine approximation for the sun's arc. In the future, I want to implement Cooper's Equation to calculate exact solar declination based on the specific latitude and longitude of the location.
