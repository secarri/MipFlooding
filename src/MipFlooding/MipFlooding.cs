using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;


namespace ImageProcessingLibrary
{
    public class MipFlooding
    {
        private static void StackMipLevels(Bitmap background, int mipLevels, Bitmap color, Bitmap alpha, int originalWidth, int originalHeight, Logger logger, bool reCompositeMip0OnTop = true)
        {
            // This takes 60% of the time, maybe it can be optimized even more. 
            Stopwatch stopwatch = Stopwatch.StartNew();

            // Start iterating over the mip levels
            Bitmap maskedColor = ImageProcessor.ApplyAlpha(color, alpha);

            try
            {
                for (int mipLevel = mipLevels - 1; mipLevel >= 0; mipLevel--)
                {
                    int tempWidth = (int)Math.Pow(2, mipLevel + 1);
                    int tempHeight = ImageProcessor.CalculateImageHeight(tempWidth, color);

                    int resW = originalWidth / tempWidth;
                    int resH = originalHeight / tempHeight;
                    if (resW < 1 || resH < 1)
                        continue;

                    using (Bitmap resizedColor = ImageProcessor.ResizeImage(maskedColor, resW, resH, System.Drawing.Drawing2D.InterpolationMode.Bilinear))
                    using (Bitmap resizedAlpha = ImageProcessor.ResizeImage(alpha, resW, resH, System.Drawing.Drawing2D.InterpolationMode.Bilinear))
                    using (Bitmap normalizedColor = ImageProcessor.NormalizeColor(resizedColor, resizedAlpha))
                    using (Bitmap combinedColor = ImageProcessor.CombineColorAndAlpha(normalizedColor, resizedAlpha))
                    using (Bitmap colorToStack = ImageProcessor.ResizeImage(combinedColor, originalWidth, originalHeight, System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor))
                    {
                        using (Graphics g = Graphics.FromImage(background))
                        {
                            g.DrawImage(colorToStack, 0, 0, colorToStack.Width, colorToStack.Height);
                        }
                    }
                }

                // Re-composite the original Mip0 color on top to preserve full fidelity
                // in opaque regions. The mip-flooded data only fills the transparent areas.
                if (reCompositeMip0OnTop)
                {
                    logger.LogInfo("--- Re-compositing Mip0 on top of mip-flooded result...");
                    using (Bitmap originalComposite = ImageProcessor.CombineColorAndAlpha(color, alpha))
                    using (Graphics g = Graphics.FromImage(background))
                    {
                        g.DrawImage(originalComposite, 0, 0, originalWidth, originalHeight);
                    }
                }
            }
            finally
            {
                maskedColor.Dispose();
            }
            
            stopwatch.Stop();
            TimeSpan elapsedTime = stopwatch.Elapsed;
            logger.LogInfo($"--- StackMipLevels Time: {elapsedTime.TotalSeconds:F6} seconds.");
        }

        public static void RunMipFlooding(string inTexColorAbsPath, string inTexAlphaAbsPath, string outAbsPath, string format, bool reCompositeMip0OnTop = true)
        {
            // Start the logger
            string loggerPath = Path.GetDirectoryName(outAbsPath);
            string loggerName = Path.GetFileNameWithoutExtension(outAbsPath);
            Logger logger = new Logger($"{loggerPath}/Logs/{loggerName}.log");
            
            // Start Mip Flooding
            logger.LogInfo($"Starting mip flooding algorithm for: {inTexColorAbsPath}");
            logger.LogInfo($"--- Re-composite Mip0: {reCompositeMip0OnTop}");
            Stopwatch stopwatch = Stopwatch.StartNew();

            using (Bitmap color = new Bitmap(inTexColorAbsPath))
            using (Bitmap alpha = new Bitmap(inTexAlphaAbsPath))
            {
                // Get output format
                ImageFormat outFormat = ImageFormatHelper.GetImageFormat(format);

                // Caching resolutions
                int colorWidth = color.Width;
                int colorHeight = color.Height;
                int alphaWidth = alpha.Width;
                int alphaHeight = alpha.Height;

                // Run validation on inputs
                if (ImageValidation.ValidateInputs(colorWidth, colorHeight, alphaWidth, alphaHeight, logger) == false)
                {
                    return;
                }

                // Get mip levels
                logger.LogInfo("--- Calculating mip map levels...");
                int getMipLevels = ImageProcessor.GetMipLevels(colorWidth, colorHeight);
                logger.LogInfo($"--- Done. Miplevels: {getMipLevels}");

                // Generate the background using the alpha mask
                logger.LogInfo("--- Generating and storing background image in memory...");
                using (Bitmap background_img = ImageProcessor.GenerateAverageColorImage(color, alpha))
                {
                    // Run stacking process
                    logger.LogInfo("--- Starting 'Stacking' process...");
                    StackMipLevels(background_img, getMipLevels, color, alpha, colorWidth, colorHeight, logger, reCompositeMip0OnTop);
                    background_img.Save(outAbsPath, outFormat);
                }
            }

            stopwatch.Stop();
            TimeSpan elapsedTime = stopwatch.Elapsed;

            // Calculate improvement
            long oldFileSize = FileUtilities.GetFileSize(inTexColorAbsPath);
            long newFileSize = FileUtilities.GetFileSize(outAbsPath);
            double changePercentage = oldFileSize > 0
                ? ((double)(newFileSize - oldFileSize) / oldFileSize) * 100.0
                : 0.0;

            if (changePercentage > 0)
            {
                logger.LogWarning($"--- Final image is {changePercentage:F2}% bigger on disk.");
            }
            else if (changePercentage < 0)
            {
                logger.LogInfo($"--- Final image is {Math.Abs(changePercentage):F2}% smaller on disk.");
            }
            else
            {
                logger.LogInfo("--- Final image size is unchanged.");
            }

            logger.LogInfo($"--- Mip Flooding Time: {elapsedTime.TotalSeconds:F6} seconds.");
        }
    }
}
