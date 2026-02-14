using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Threading.Tasks;


namespace ImageProcessingLibrary
{
    public class ImageProcessor
    {
        public static int GetMipLevels(int imageWidth, int imageHeight)
        {
            int shortSide = Math.Min(imageWidth, imageHeight);
            if (shortSide <= 1)
                return 0;

            // Exact integer bit-shift count — avoids floating-point precision
            // issues that Math.Log can introduce for large power-of-two sizes.
            int levels = 0;
            int s = shortSide;
            while (s > 1)
            {
                s >>= 1;
                levels++;
            }

            return levels;
        }

        public static int CalculateImageHeight(int imageWidth, Bitmap image)
        {
            // Calculate the width percentage relative to the original image width
            float widthPercent = (float)imageWidth / image.Width;

            // Calculate the new height based on the width percentage and the original image height
            int newHeight = (int)(image.Height * widthPercent);

            return newHeight;
        }

        public static Bitmap ResizeImage(Bitmap image, int newWidth, int newHeight, System.Drawing.Drawing2D.InterpolationMode interpolationMode)
        { 
            Bitmap resizedImage = new Bitmap(newWidth, newHeight);

            using (Graphics g = Graphics.FromImage(resizedImage))
            {
                g.InterpolationMode = interpolationMode;
                g.DrawImage(image, 0, 0, newWidth, newHeight);
            }

            return resizedImage;
        }

        public static Bitmap GenerateAverageColorImage(Bitmap inputBitmap, Bitmap maskBitmap)
        {
            int width = inputBitmap.Width;
            int height = inputBitmap.Height;

            if (maskBitmap.Width != width || maskBitmap.Height != height)
            {
                throw new ArgumentException(
                    $"Input ({width}x{height}) and mask ({maskBitmap.Width}x{maskBitmap.Height}) must have the same dimensions.",
                    nameof(maskBitmap));
            }

            int pixelCount = 0;
            long sumR = 0, sumG = 0, sumB = 0;

            BitmapData bmpData = inputBitmap.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData maskData = maskBitmap.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);

            unsafe
            {
                byte* colorPtr = (byte*)bmpData.Scan0;
                byte* maskPtr = (byte*)maskData.Scan0;

                for (int y = 0; y < height; y++)
                {
                    for (int x = 0; x < width; x++)
                    {
                        int colorIndex = y * bmpData.Stride + x * 4;
                        int maskIndex = y * maskData.Stride + x * 4;

                        // Use the mask to determine if the pixel is visible
                        byte maskValue = maskPtr[maskIndex];
                        if (maskValue == 0)
                            continue;

                        byte b = colorPtr[colorIndex];
                        byte g = colorPtr[colorIndex + 1];
                        byte r = colorPtr[colorIndex + 2];

                        sumR += r;
                        sumG += g;
                        sumB += b;
                        pixelCount++;
                    }
                }
            }

            inputBitmap.UnlockBits(bmpData);
            maskBitmap.UnlockBits(maskData);

            if (pixelCount == 0)
            {
                // Return a full-size black bitmap when every pixel is masked out
                Bitmap fallback = new Bitmap(width, height);
                using (Graphics gfx = Graphics.FromImage(fallback))
                {
                    gfx.Clear(Color.Black);
                }
                return fallback;
            }

            int avgR = (int)(sumR / pixelCount);
            int avgG = (int)(sumG / pixelCount);
            int avgB = (int)(sumB / pixelCount);

            // Create a new bitmap filled with the average color
            var avgColor = Color.FromArgb(avgR, avgG, avgB);
            Bitmap result = new Bitmap(width, height);

            using (Graphics gfx = Graphics.FromImage(result))
            {
                gfx.Clear(avgColor);
            }

            return result;
        }

        public static Bitmap ApplyAlpha(Bitmap color, Bitmap alpha)
        {
            int width = color.Width;
            int height = color.Height;
            Bitmap result = new Bitmap(width, height, PixelFormat.Format32bppArgb);

            // Lock bits for direct access
            BitmapData colorData = color.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData alphaData = alpha.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData resultData = result.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);

            unsafe
            {
                // Pointers to the start of the image data
                byte* colorPtr = (byte*)colorData.Scan0;
                byte* alphaPtr = (byte*)alphaData.Scan0;
                byte* resultPtr = (byte*)resultData.Scan0;

                int colorStride = colorData.Stride;
                int alphaStride = alphaData.Stride;
                int resultStride = resultData.Stride;

                // Process each pixel in parallel
                Parallel.For(0, height, y =>
                {
                    byte* colorRow = colorPtr + y * colorStride;
                    byte* alphaRow = alphaPtr + y * alphaStride;
                    byte* resultRow = resultPtr + y * resultStride;

                    for (int x = 0; x < width; x++)
                    {
                        int colorIndex = x * 4;
                        int resultIndex = x * 4;

                        // Extract color and alpha values
                        byte colorR = colorRow[colorIndex + 2];
                        byte colorG = colorRow[colorIndex + 1];
                        byte colorB = colorRow[colorIndex + 0];
                        byte alphaA = alphaRow[colorIndex + 0];  // Assuming the alpha channel is in the same position in alpha image

                        // Apply the alpha mask to the color pixel
                        resultRow[resultIndex + 3] = 255; // Alpha channel
                        resultRow[resultIndex + 2] = (byte)((colorR * alphaA + 127) / 255);
                        resultRow[resultIndex + 1] = (byte)((colorG * alphaA + 127) / 255);
                        resultRow[resultIndex + 0] = (byte)((colorB * alphaA + 127) / 255);
                    }
                });
            }

            // Unlock bits
            color.UnlockBits(colorData);
            alpha.UnlockBits(alphaData);
            result.UnlockBits(resultData);

            return result;
        }

        public static Bitmap NormalizeColor(Bitmap color, Bitmap mask)
        {
            int width = color.Width;
            int height = color.Height;
            Bitmap result = new Bitmap(width, height, PixelFormat.Format32bppArgb);

            // Lock bits for color and mask images
            BitmapData colorData = color.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData maskData = mask.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData resultData = result.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);

            int colorStride = colorData.Stride;
            int maskStride = maskData.Stride;
            int resultStride = resultData.Stride;

            unsafe
            {
                byte* colorPtr = (byte*)colorData.Scan0;
                byte* maskPtr = (byte*)maskData.Scan0;
                byte* resultPtr = (byte*)resultData.Scan0;

                Parallel.For(0, height, y =>
                {
                    byte* colorRow = colorPtr + y * colorStride;
                    byte* maskRow = maskPtr + y * maskStride;
                    byte* resultRow = resultPtr + y * resultStride;

                    for (int x = 0; x < width; x++)
                    {
                        int index = x * 4;

                        byte colorR = colorRow[index + 2];
                        byte colorG = colorRow[index + 1];
                        byte colorB = colorRow[index + 0];
                        byte maskR = maskRow[index + 2];
                        byte maskG = maskRow[index + 1];
                        byte maskB = maskRow[index + 0];

                        // Avoid division by zero using conditional operator
                        resultRow[index + 2] = maskR == 0 ? (byte)0 : (byte)Math.Min(255, (colorR * 255) / maskR);
                        resultRow[index + 1] = maskG == 0 ? (byte)0 : (byte)Math.Min(255, (colorG * 255) / maskG);
                        resultRow[index + 0] = maskB == 0 ? (byte)0 : (byte)Math.Min(255, (colorB * 255) / maskB);

                        // Set alpha channel to fully opaque
                        resultRow[index + 3] = 255;
                    }
                });
            }

            // Unlock bits
            color.UnlockBits(colorData);
            mask.UnlockBits(maskData);
            result.UnlockBits(resultData);

            return result;
        }

        public static Bitmap CombineColorAndAlpha(Bitmap colorMap, Bitmap mask)
        {
            int width = colorMap.Width;
            int height = colorMap.Height;
            Bitmap result = new Bitmap(width, height, PixelFormat.Format32bppArgb);

            // Lock the bits for color map, mask, and result images
            BitmapData colorData = colorMap.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData maskData = mask.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData resultData = result.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);

            unsafe
            {
                byte* colorPtr = (byte*)colorData.Scan0;
                byte* maskPtr = (byte*)maskData.Scan0;
                byte* resultPtr = (byte*)resultData.Scan0;

                int colorStride = colorData.Stride;
                int maskStride = maskData.Stride;
                int resultStride = resultData.Stride;

                // Parallel processing of image rows
                Parallel.For(0, height, y =>
                {
                    byte* colorRow = colorPtr + y * colorStride;
                    byte* maskRow = maskPtr + y * maskStride;
                    byte* resultRow = resultPtr + y * resultStride;

                    for (int x = 0; x < width; x++)
                    {
                        int index = x * 4;

                        // Copy the color channels (R, G, B) from the color map
                        resultRow[index + 0] = colorRow[index + 0]; // B
                        resultRow[index + 1] = colorRow[index + 1]; // G
                        resultRow[index + 2] = colorRow[index + 2]; // R

                        // Set the alpha channel from the mask (assuming grayscale)
                        resultRow[index + 3] = maskRow[index + 0];
                    }
                });
            }

            // Unlock the bits
            colorMap.UnlockBits(colorData);
            mask.UnlockBits(maskData);
            result.UnlockBits(resultData);

            return result;
        }
    }
}
