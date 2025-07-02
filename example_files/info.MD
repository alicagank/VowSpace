# Examples!

In this directory, there are two Excel files and two audio files.

---

## Lobanov Normalization Example

In the Excel file titled **"Speaking Fundamental Frequency and Vowel Formant Frequencies: Effects on Perception of Gender"**, you will find perhaps one of the most well-known descriptions of the vowel inventory of Standard American English.

Try and normalize the results using the **Lobanov method** found under the `Normalization` tab in the menu bar, and see what happens:

- You'll notice the gender difference is no longer a significant factor (or at least greatly minimized).
- What remains are the **sociolinguistic differences** between the study participants!

**This data is from:**

- Gelfer, M. P., & Bennett, Q. E. (2013). *Speaking fundamental frequency and vowel formant frequencies: Effects on perception of gender*. *Journal of Voice, 27*(5), 556–566.
- Hillenbrand, J., Getty, L. A., Clark, M. J., & Wheeler, K. (1995). *Acoustic characteristics of American English vowels*. *The Journal of the Acoustical Society of America, 97*(5), 3099–3111.
- Peterson, G. E., & Barney, H. L. (1952). *Control methods used in a study of the vowels*. *The Journal of the Acoustical Society of America, 24*(2), 175–184.

---

## Plotting Turkish Vowels

We will use the dataset `turkish_vowels.xlsx` for this example.

This data is based on:

> Korkmaz, Y., & Boyacı, A. (2018). *Classification of Turkish Vowels Based on Formant Frequencies*. 2018 International Conference on Artificial Intelligence and Data Processing (IDAP), 1–4. [https://doi.org/10.1109/IDAP.2018.8620877](https://doi.org/10.1109/IDAP.2018.8620877)

The dataset includes realizations of the Turkish vowels: `/a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/, /y/`  
(I kept the phonological transcriptions in the dataset as-is.)

### Visualizing in VowSpace

- Open the file in VowSpace.
- Enable `Show Grids` and `Show Labels for Vowel(s)` to display the basic vowel scatterplot.

To create a quadrilateral-like layout:

- Use the `Connect with Qhull` action in the menu.

To visualize individual vowel articulation points:

- Activate the `Group by Vowel` action to group by phoneme rather than speaker or language.

When the dataset is sparse, ellipses are helpful:

- Enable the `Connect with Ellipse` action.

### Ellipse Logic

- The **covariance matrix** captures the variance and covariance of data points.
- **Eigenvalues** give the **lengths** of the ellipse axes.
- **Eigenvectors** give the **directions** of the axes.

Ellipse logic: The covariance matrix captures the variance and covariance of the data points in your subset, the eigenvalues give the length of the principal axes of the ellipse and the eigenvectors give the direction of the principal axes.

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
## Get Formants From My Voice and Plot Them!

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