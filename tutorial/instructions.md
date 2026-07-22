# Tutorials!

Welcome! In this directory, you’ll find two Excel files, two audio recordings, and this instruction file. These tutorials are here to help you get started with **VowSpace** and make the most of its core features. (If you have any suggestions or if anything doesn’t work as expected, please let me know!)

---

### 🔍 What’s Inside?

#### 🇹🇷 Tutorial #1: Plotting Turkish vowels
Visualise Turkish vowels from an acoustic study using ellipses. Learn how to group your data by vowel, interpret the vowel space in articulatory terms, and understand the covariance-and-eigenvalue logic behind the ellipses.

#### 🎙️ Tutorial #2: Plotting my voice and comparing it to another person's
Analyse my voice! Load the provided recordings (`cagan.wav` and `ozlem.wav`) into the **Audio Analysis Tools**, extract formant values, add them to your scatterplot, and compare two speakers. I guess this is the most fun and interactive way to learn how VowSpace works with real-world audio.

#### ✅ Tutorial #3: Lobanov normalisation tutorial
Use a classic American English dataset to learn how to normalise vowel formants using the **Lobanov method**. See how normalisation minimises gender-related variation and brings out sociolinguistic patterns.

---

I hope these tutorials make using VowSpace intuitive, and maybe even a little fun. :)

---

## #1 Plotting Turkish vowels

We will use the dataset `kaya-yagli-2026.xlsx` for this example.

This dataset is based on the raw data from one of my papers investigating the acoustic characteristics of Turkish vowels.

The dataset includes realisations of the Turkish vowels: `/a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/, /y/`  
(I kept the phonological transcriptions in the dataset as-is.)

In this example, we aim to visualise the data to gain a clearer understanding of the Turkish vowel space.

1. Let’s launch VowSpace.

![Turkish vowels tutorial – image 1](images/tr1.png)

2. We can use the `File -> Import Data from Dataset` function to locate and load our data. Simply click on the file titled `kaya-yagli-2026.xlsx`.

![Turkish vowels tutorial – image 2](images/tr2.png)

3. When done correctly, this should bring up the `DataFrame Editor`. Here, you may inspect the raw data and make edits if necessary.

![Turkish vowels tutorial – image 3](images/tr3.png)

4. Close the `DataFrame Editor`, and you will see the individual vowels as points in the main window. It should look something like this:

![Turkish vowels tutorial – image 4](images/tr4.png)

From here, we need to make a few adjustments to the visualisation to make the data more interpretable and the plot better-looking. :)

5. Choose `Visualization / Normalization Settings...` under the `Options` menu.

![Turkish vowels tutorial – image 5](images/tr5.png)

6. Now your screen should look something like this:

![Turkish vowels tutorial – image 6](images/tr6.png)

7. Let’s have a look at each individual vowel before making the plot more interpretable, just to see what we are working with.

Use the `Show vowel labels` method to add vowel labels to each point!

![Turkish vowels tutorial – image 7](images/tr9.png)

A bit crammed, isn't it? :)

8. Here's what we do:

    8.1. `Group by Vowel`: We group our data by vowel instead of by speaker because the dataset includes 20 speakers, but we are interested in the individual vowels.

    8.2. `Connect with Ellipse(s)`: We visualise the vowels using ellipses. This gives us a clearer representation than coloured points alone and helps us understand the area each vowel occupies in the vowel space.

    8.3. `Show center labels`: We display the vowel labels at the centre of the ellipses instead of over each individual point.

If everything went well, your screen should look something like this:

![Turkish vowels tutorial – image 8](images/tr7.png)

9. Let's make it look prettier. :)

You can use the `Ellipse outline only` method, since we are interested in the vowel spaces rather than each individual vowel token.

We can also set the `Point size` to `20`, since there are many points.

We can also lower the `Point alpha` value, which controls the transparency of the points, to make the ellipses more prominent.

![Turkish vowels tutorial – image 9](images/tr8.png)

10. Now we can move on to saving our plot using `File -> Export as...`.

![Turkish vowels tutorial – image 10](images/tr10.png)

11. This should bring up a preview window titled `Export Plot`. Here, you may adjust the export settings. For our purposes, you can keep the default settings, but feel free to play with them.

![Turkish vowels tutorial – image 11](images/tr11.png)

And here are our results! :)

![Turkish vowels tutorial – image 12](images/tr12.jpeg)

### Ellipse Logic

* The **covariance matrix** captures the variance and covariance of the data points.
* **Eigenvalues** determine the **lengths** of the ellipse axes.
* **Eigenvectors** determine the **directions** of the axes.

I learned this method from Joey Stanley’s *Making Vowel Plots in R (Part 1)*. It’s an awesome resource if you’re working on vowel visualisation!

```python
# This ensures that the eigenvalues and corresponding eigenvectors are
# ordered correctly, typically from the largest to the smallest eigenvalue.
eigvals, eigvecs = np.linalg.eigh(cov)
order = eigvals.argsort()[::-1]
eigvals, eigvecs = eigvals[order], eigvecs[:, order]
```

Suppose you have a dataset with a covariance matrix $\Sigma$. The eigenvectors of $\Sigma$ might be:

$$
\mathbf{v}_1 = \begin{pmatrix} 1 \ 0 \end{pmatrix}, \quad
\mathbf{v}_2 = \begin{pmatrix} 0 \ 1 \end{pmatrix}
$$

These eigenvectors indicate that the principal directions of the data spread lie along the x- and y-axes. If the corresponding eigenvalues are:

$$
\lambda_1 = 4, \quad \lambda_2 = 1
$$

then the lengths of the axes of the ellipse are:

$$
2\sqrt{4} = 4, \quad \text{and} \quad 2\sqrt{1} = 2
$$

The chi-squared distribution is used to scale the eigenvalues and determine the size of the ellipse. In VowSpace, you can adjust the percentage of the data that the ellipse is intended to cover. The default coverage is **67%**, which corresponds to a cumulative probability of `0.67`.

The selected coverage percentage is converted into a scale factor using a chi-squared distribution with two degrees of freedom:

```python
scale_factor = chi2.ppf(0.67, df=2)
```

Here, `0.67` represents the default coverage. When you change the ellipse coverage setting in VowSpace, this value is replaced by the selected percentage expressed as a proportion. For example, a coverage of 95% would use `0.95`.


---

## #2 Plotting my voice and comparing it to another person's

I am a native Turkish speaker, and Turkish has eight vowels: /a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/, /y/.

I’ve included a recording, `cagan.wav`, in which I pronounce all of them aloud. I also asked a female friend of mine to do the same in `ozlem.wav`.

1. Let’s launch VowSpace and click the `Audio Analysis Tools` button to open the `Audio Analysis Tools` window. This is a spectrogram-based tool that lets you do a number of things with a sound file.

![Voice tutorial – image 1](images/voice1.png)

2. An empty plot should appear on your screen.

![Voice tutorial – image 2](images/voice2.png)

3. To load a sound file into the `Audio Analysis Tools` window, use `File -> Read from Audio File`.

![Voice tutorial – image 3](images/voice3.png)

4. After you select `cagan.wav` in your file manager, the sound file should load and a spectrogram should appear. I repeat the full vowel set four times, and you should be able to see the vowels as darker patches.

![Voice tutorial – image 4](images/voice4.png)

We need to be able to see the formant frequencies to work on them properly. :)

5. Use the `Show Formants` method to show the F1 and F2 frequencies.

![Voice tutorial – image 5](images/voice5.png)

![Voice tutorial – image 6](images/voice6.png)

6. Now your window should look something like this:

![Voice tutorial – image 7](images/voice7.png)

As you can see, the formant lines for each individual vowel are quite clear. For convenience, let’s choose one set of eight vowels first:

7. You can do this by selecting the magnifying-glass icon and choosing an area to zoom into, like so:

![Voice tutorial – image 8](images/voice8.gif)

8. Here, the vowels are, respectively, /a/, /e/, /ɯ/, /i/, /o/, /œ/, /u/, and /y/.

![Voice tutorial – image 9](images/voice9.png)

Click approximately in the middle of a formant line, then right-click to add its value to the main VowSpace window!

9. VowSpace should automatically add the name of the sound file and the formant values. You only need to enter the vowel label and press the `Add Data` button or hit Enter.

![Voice tutorial – image 10](images/voice10.png)

Your data should now appear as points of the same colour, as in the image above.

10. Now let’s make the plot a little more interpretable using `Options -> Visualization / Normalization Settings`.

![Voice tutorial – image 11](images/voice11.png)

Using `Show vowel labels` and `Show speaker labels` makes it easier to see where each vowel is located in the vowel space.

Using `Connect with Qhull(s)`, you can connect the points with a convex hull to see the vowel space more clearly.

![Voice tutorial – image 12](images/voice12.png)

I’ve also included another file, `ozlem.wav`, containing a similar recording from a female friend of mine. Try the same steps with this file and compare the results!

![Voice tutorial – image 13](images/voice13.png)

You can also add a legend:

![Voice tutorial – image 14](images/voice14.png)

Apply `Lobanov Normalization` to minimise gender-related variation and compare the two speakers more clearly.

`Normalization / Conversion -> Lobanov Normalization`

![Voice tutorial – image 15](images/voice15.png)

I hope this helps!

## Ethics and Data Statement

The human-participant data (i.e., the audio recordings) provided in this tutorial were collected in accordance with the ethical principles of the Declaration of Helsinki. The study received formal approval from the Hacettepe University Social Sciences and Humanities Ethics Board on 10 September 2024 (Ref: 2024/16). All participants provided written informed consent for their voice data to be recorded and used for research and instructional purposes.

- **Ethics Committee**: Hacettepe University Social Sciences and Humanities Ethics Board
- **Approval Date**: 16.08.2024
- **Approval Number**: E-28297300-900-00003711909

---

## #3 Lobanov normalisation tutorial

In the Excel file titled **"Speaking Fundamental Frequency and Vowel Formant Frequencies: Effects on Perception of Gender"**, you will find perhaps one of the most well-known descriptions of the vowel inventory of Standard American English.

Try normalising the results using the **Lobanov method** and see what happens:

- You’ll notice that gender-related variation is greatly minimised.
- The **sociolinguistic differences** between the study participants become much easier to see!

### Step-by-Step Instructions

1. **Launch VowSpace**.

![Lobanov tutorial – image 1](images/lob1.png)

2. Under the `File` menu in the menu bar, click `Import Data from Dataset`.

![Lobanov tutorial – image 2](images/lob2.png)

3. Locate and select the file named `speaking_fundamental_fequency_and_vowel_formant_frequencies_effects_on_perception_of_gender.xlsx`. The **DataFrame Editor** will open. Here, you can inspect the data and then close the editor window.

![Lobanov tutorial – image 3](images/lob3.png)

4. After you close the DataFrame Editor, you will see the vowels plotted as coloured dots in the main window.

![Lobanov tutorial – image 4](images/lob4.png)

5. Now let’s make the data more interpretable. Click `Visualization / Normalization Settings...` under the `Options` menu.

![Lobanov tutorial – image 5](images/lob5.png)

6. Your screen should now look something like this:

![Lobanov tutorial – image 6](images/lob6.png)

7. Let’s have a look at what each individual dot represents. To do this, we can use `Show vowel labels` and `Show speaker labels`. This should give us a basic idea of the data.

![Lobanov tutorial – image 7](images/lob7.png)

8. Enabling `Connect with Qhull(s)` connects the dots associated with each speaker. Showing centre labels also gives us a cleaner view.

Since VowSpace groups the data by speaker by default, the centre labels are automatically associated with the speakers. However, you can also try `Group by Vowel` and see what it does. :)

![Lobanov tutorial – image 8](images/lob8.png)

Let's give ourselves some more space to work with. :)

![Lobanov tutorial – image 9](images/lob9.png)

9. Now for the cool part: apply **Lobanov Normalization**.  

That is: `Normalization / Conversion -> Lobanov Normalization`

![Lobanov tutorial – image 10](images/lob10.png)

This converts all vowel-formant values into z-scores for each speaker. You can always goof around with the other normalisation methods, too! (You can see the numerical results in the DataFrame Editor in real time!)

You should now be able to see your normalised data. Notice how /i/ stays almost the same, while /e/ and /a/ are affected more strongly. Pretty interesting, right?


10. To give the plot a more structured look, you can also enable `Show Legend`.

The scatterplot with the legend enabled:

![Lobanov tutorial – image 11](images/lob11.png)

And after normalisation:

![Lobanov tutorial – image 12](images/lob12.png)

11. Now we can save our visualised plot!

Use `File -> Export as...` to save the visualised plot.

AND HERE IS OUR RESULT! ⭐️

![Lobanov tutorial - image 13](images/lob13.png)


### Goal

This dataset includes two male and two female speakers from different backgrounds. Our aim here is **not** to highlight biological differences (because we’re not sexists, we’re linguists), but to showcase **sociophonetic variation**.

**Et voilà!**  
You now have a publication-ready, normalised vowel plot using the Lobanov method.

---

### References

> Gelfer, M. P., & Bennett, Q. E. (2013). *Speaking fundamental frequency and vowel formant frequencies: Effects on perception of gender*. *Journal of Voice, 27*(5), 556–566.
>
> Hillenbrand, J., Getty, L. A., Clark, M. J., & Wheeler, K. (1995). *Acoustic characteristics of American English vowels*. *The Journal of the Acoustical Society of America, 97*(5), 3099–3111.
>
> Peterson, G. E., & Barney, H. L. (1952). *Control methods used in a study of the vowels*. *The Journal of the Acoustical Society of America, 24*(2), 175–184.

---

