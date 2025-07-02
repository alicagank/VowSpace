# 📚 Tutorials!

Welcome! In this directory, you’ll find two Excel files, two audio recordings, and this instruction file. These tutorials are here to help you get started with **VowSpace** and make the most of its core features.

---

### 🔍 What's Inside?

#### ✅ Tutorial #1: Lobanov normalization tutorial
Use a classic American English dataset to learn how to normalize vowel formants using the **Lobanov method**. See how normalization minimizes gender-based variation and brings out sociolinguistic patterns. Pretty useful for researchers preparing publishable plots.

#### 🇹🇷 Tutorial #2: Plotting Turkish vowels
Visualize Turkish vowels from an acoustic study using Qhulls and ellipses. Learn how to group by vowel, interpret articulatory space, and apply ellipse logic using covariance and eigenvalues. A great hands-on example of vowel space visualization techniques.

#### 🎙️ Tutorial #3: Plotting my voice
Analyze my voice! Load provided recordings (`cagan.mp3`, `ozlem.mp3`) into the **Audio Analysis Tool**, extract formants, and add them to your scatterplot. I guess this is the most fun and interactive way to learn how VowSpace works with real-world audio.

---

I hope these tutorials make using VowSpace intuitive, and maybe even a little fun.

---

## #1 Lobanov normalization tutorial

In the Excel file titled **"Speaking Fundamental Frequency and Vowel Formant Frequencies: Effects on Perception of Gender"**, you will find perhaps one of the most well-known descriptions of the vowel inventory of Standard American English.

Try and normalize the results using the **Lobanov method** found under the `Normalization` tab in the menu bar, and see what happens:

- You'll notice the gender difference is no longer a significant factor (or at least greatly minimized).
- What remains are the **sociolinguistic differences** between the study participants!

### Step-by-Step Instructions

1. **Launch VowSpace**.

![Step 1 - Run VowSpace](images/1.png)

2. Under the `File` menu in the menubar, click `Import Data from Spreadsheet`.

![Step 2 - Import the data](images/2.png)

3. Locate the file named: speaking_fundamental_fequency_and_vowel_formant_frequencies_effects_on_perception_of_gender.xlsx


4. The **DataFrame Editor** will open. Here you can inspect the data and then close the editor window.

![Step 4 - DataFrame Editor](images/3.png)

5. You will now see the vowels plotted as colored dots. By default, VowSpace groups them by speaker.  
(You can change this in the settings, but for this tutorial we keep it grouped by speaker.)

![Step 5 - See the dots](images/4.png)

6. For better clarity, use the `Connect with Qhull(s)` option under the `Visualization Options` menu.

![Step 6 - Qhull options](images/5.png)

Now your data should look like this:
![Qhull enabled](images/6.png)

7. Now enable the legend to show speaker information. Go to:

`Visualization Options → Legend Options → Show Legend`

![Step 7 - Legend options](images/7.png)

Optionally, resize the scatterplot window for better visibility.

![Scatterplot with the Legend](images/8.png)

9. Now the cool part: apply the **Lobanov Normalization**.  
Go to:

`Data Options → Normalize → Lobanov Normalization`

![Step 8 - Apply normalization](images/9.png)

This will convert all vowel formant values to z-scores per speaker.

Here's your normalized data:

![Normalized data](images/10.png)

10. To give the plot a more structured look, you can also use:

`Visualization Options → Show Grids`

![Step 9](images/11.png)

The scatterplot with the grids enabled:
![Grids enabled](images/12.png)

11. Now we can save our visualized data!

Use the `File → Save as...` option to save the visaulized data!

![Step 10 - Saving the scatterplot](images/13.png)

AND HERE ARE OUR RESULTS! ⭐️

![Results!](images/14.jpg)

### Goal

This dataset includes 2 male and 2 female speakers from different backgrounds. Our aim here is **not** to highlight biological differences (because we're not sexists, we're linguists), but to showcase **sociophonetic variation**.

**Et voilà!**  
You now have a publication-ready, normalized vowel plot using the Lobanov method.

---

### 📚 References

> Gelfer, M. P., & Bennett, Q. E. (2013). *Speaking fundamental frequency and vowel formant frequencies: Effects on perception of gender*. *Journal of Voice, 27*(5), 556–566.
> 
> Hillenbrand, J., Getty, L. A., Clark, M. J., & Wheeler, K. (1995). *Acoustic characteristics of American English vowels*. *The Journal of the Acoustical Society of America, 97*(5), 3099–3111.
> 
> Peterson, G. E., & Barney, H. L. (1952). *Control methods used in a study of the vowels*. *The Journal of the Acoustical Society of America, 24*(2), 175–184.


---

## #2 Plotting Turkish vowels

We will use the dataset `turkish_vowels.xlsx` for this example.

This data is based on:

> Korkmaz, Y., & Boyacı, A. (2018). *Classification of Turkish Vowels Based on Formant Frequencies*. 2018 International Conference on Artificial Intelligence and Data Processing (IDAP), 1–4. [https://doi.org/10.1109/IDAP.2018.8620877](https://doi.org/10.1109/IDAP.2018.8620877)

The dataset includes realizations of the Turkish vowels: `/a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/, /y/`  
(I kept the phonological transcriptions in the dataset as-is.)

With this example, we aim to visualize the data from a great paper on vowels in Turkish to gain a clearer understanding of the vowel space of Turkish.

The dataset is composed of different realizations of the vowels /a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/ and /y/ (I kept the phonologic transcriptions in the dataset as is).
When imported to VowSpace with the `Show Grids` and `Show Labels for Vowel(s)` options activated, our data looks like this:

![Vowel Space with Grids and Labels](images/15.jpg)

To achieve a more conventional, quadrilateral-like view of the vowel space, we use the `Connect with Qhull` action:

![Qhull Connection - 1](images/16.jpg)

![Qhull Connection - 2](images/17.jpg)

In some cases, we might want to see where individual vowels are articulated. We use the `Group by Vowel` action to take unique phonemes into account rather than the speaker/language:

![Grouped by Vowel](images/18.jpg)

Using Qhulls, we can see the places of articulation clearer:

![Qhulls - Places of Articulation](images/19.jpg)

Considering the limited number of data, using ellipses to visualize these may be a better option:

![Ellipses Visualization](images/20.jpg)


### Ellipse Logic

- The **covariance matrix** captures the variance and covariance of data points.
- **Eigenvalues** give the **lengths** of the ellipse axes.
- **Eigenvectors** give the **directions** of the axes.

The covariance matrix captures the variance and covariance of the data points in your subset, the eigenvalues give the length of the principal axes of the ellipse and the eigenvectors give the direction of the principal axes.

I learned this method from:
Joey Stanley – Making Vowel Plots in R (Part 1). It's an awesome resource if you’re working on vowel visualization!


```python
#This ensures the eigenvalues and corresponding eigenvectors are ordered correctly, typically from largest to smallest eigenvalue.
eigvals, eigvecs = np.linalg.eigh(cov)
order = eigvals.argsort()[::-1]
eigvals, eigvecs = eigvals[order], eigvecs[:, order]
```
Suppose you have a dataset with a covariance matrix $\Sigma$. The eigenvectors of $\Sigma$ might be:

$$
\mathbf{v}_1 = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad
\mathbf{v}_2 = \begin{pmatrix} 0 \\ 1 \end{pmatrix}
$$

These eigenvectors indicate that the principal directions of the data spread are along the x-axis and y-axis.  
If the corresponding eigenvalues are:

$$
\lambda_1 = 4, \quad \lambda_2 = 1
$$

Then, the lengths of the axes of the ellipse are:

$$
2\sqrt{4} = 4, \quad \text{and} \quad 2\sqrt{1} = 2
$$

The chi-squared distribution is used to scale the eigenvalues to create a confidence ellipse. The function calculates the value from the chi-squared distribution with 2 degrees of freedom that corresponds to a cumulative probability of 0.67. This value is then used to scale the eigenvalues to determine the size of the ellipse.

```python
scale_factor = chi2.ppf(0.67, df=2)
```
---
## #3 Get formants from my voice and plot them!

I am a native Turkish speaker, and in Turkish, we have 8 vowels: /a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/, /y/.

I’ve included a recording (cagan.mp3) where I pronounce all of them aloud.

Steps:
- Open the Audio Analysis Tool in VowSpace.
- On the menu bar, click Read from audio file.
- Locate and select the file cagan.mp3.

Once the application has read the audio file:

- A spectrogram will appear.
- Use the Show formants toggle to display formants.
- Right-click in the middle of a vowel region to add it to the main visualizer (you need to type in the vowel only, the speaker is automatically added!)

I’ve also included another file: ozlem.mp3. It contains a similar recording from a female speaker friend of mine. Try the same steps with this file and compare the results!

You may also try and use the file asc-diff.xlsx. It contains the formant frequencies in the cagan.wav and ozlem.wav files along with a third speaker! You can access this file by the 'Read from Excel' on the menu bar.

I hope these will be of help!