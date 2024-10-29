using ClosedXML.Excel;
using HtmlAgilityPack;
using IniParser;
using IniParser.Model;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;

namespace EdgarArchiveDownloader
{
    class Program
    {
        static void Main(string[] args)
        {
            

            string excelTemplate = "format.xlsx";
            var parser = new FileIniDataParser();
            IniData data = null;
            List<string> validationErrors = new List<string>();

            try
            {
                data = parser.ReadFile("config.ini");
            }
            catch (Exception ex)
            {
                validationErrors.Add($"Error reading config.ini: {ex.Message}");
            }

            

            // Reading paths from config.ini
            string outPath = GetValue(data?["Paths"]?["OUT_PATH"], "OUT_PATH", validationErrors);
            string formMappingPath = GetValue(data?["Paths"]?["FORM_MAPPING"], "FORM_MAPPING", validationErrors);
            string cikListPath = GetValue(data?["Paths"]?["CIK_LIST"], "CIK_LIST", validationErrors);

            // Reading options from config.ini
            string startDateInput = GetValue(data?["OPTIONS"]?["START_DATE"], "START_DATE", validationErrors);
            string endDateInput = GetValue(data?["OPTIONS"]?["END_DATE"], "END_DATE", validationErrors);

            string keywordPath = GetValue(data?["Paths"]?["KEY_WORDS"], "KEY_WORDS", validationErrors);

            // Validate date format
            DateTime startDate, endDate;
            bool isValidStartDate = DateTime.TryParseExact(startDateInput, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out startDate);
            bool isValidEndDate = DateTime.TryParseExact(endDateInput, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out endDate);


            bool downloadOnlyKeywordMatch = true;
            bool.TryParse(GetValue(data?["OPTIONS"]?["DOWNLOAD_ONLY_KEYWORD_MATCH"], "DOWNLOAD_ONLY_KEYWORD_MATCH", validationErrors), out downloadOnlyKeywordMatch);
            bool setHyperlinksLocal = false;
            bool.TryParse(GetValue(data?["OPTIONS"]?["SET_HYPERLINKS_TO_LOCALFILE"], "SET_HYPERLINKS_TO_LOCALFILE", validationErrors),out setHyperlinksLocal);
            if (!isValidStartDate || !isValidEndDate)
            {
                validationErrors.Add("Invalid date format in config.ini. Please use yyyy-MM-dd format.");
            }

            // Validate file paths and directory existence
            ValidateDirectory(outPath, "OUT_PATH", validationErrors);
            ValidateFilePath(formMappingPath, "FORM_MAPPING", validationErrors);
            ValidateFilePath(cikListPath, "CIK_LIST", validationErrors);
            ValidateFilePath(keywordPath, "KEY_WORDS", validationErrors);

            // If there are validation errors, log them and exit
            if (validationErrors.Any())
            {
                Console.WriteLine("Configuration errors found:");
                foreach (var error in validationErrors)
                {
                    Console.WriteLine($"- {error}");
                }
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
                Environment.Exit(1);
            }
            List<string> lstKeywords = File.ReadAllLines(keywordPath).ToList();
            List<FormMapping> formMappings = ReadFormMappings(formMappingPath);
            List<string> lstCik = File.ReadAllLines(cikListPath)
                                       .Select(cik => cik.TrimStart('0'))
                                       .ToList();
            List<string> archiveLinks = GetArchiveLinks(startDate, endDate);

            string outputIdx = Path.Combine(outPath, "masterIdx");
            if(!Directory.Exists(outputIdx))
                Directory.CreateDirectory(outputIdx);


            string pathForExcel = excelTemplate;
            var workbook = new XLWorkbook(pathForExcel);
            var ws1 = workbook.Worksheet("Sheet1");
            int curRow = 2;
            string outFileName = Path.Combine(outPath,DateTime.Now.ToShortDateString().Replace("/", "-")+"_EdgarInfo.xlsx");
            if(File.Exists(outFileName))
                File.Delete(outFileName);
            using (HttpClient client = new HttpClient())
            {
                // Set headers to avoid 403 Forbidden error
                client.DefaultRequestHeaders.UserAgent.ParseAdd("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36");
                client.DefaultRequestHeaders.Add("Sec-Ch-Ua", "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"");
                client.DefaultRequestHeaders.Add("Sec-Ch-Ua-Mobile", "?0");
                client.DefaultRequestHeaders.Add("Sec-Ch-Ua-Platform", "\"Windows\"");
                client.DefaultRequestHeaders.Add("Upgrade-Insecure-Requests", "1");

                foreach (var link in archiveLinks)
                {
                    string fileName = GetFileNameFromLink(link);
                    string filePath = Path.Combine(outputIdx, fileName);

                    int yearIndex = link.IndexOf("/edgar/full-index/") + "/edgar/full-index/".Length;
                    string year = link.Substring(yearIndex, 4); // Assuming the year is always 4 characters (e.g., "2021")

                    int qtrIndex = link.LastIndexOf("QTR") + "QTR".Length;
                    string qtr = "QTR-" + link.Substring(qtrIndex, 1);
                    if (!File.Exists(filePath))
                    {
                        string idxLink = link.TrimEnd('/') + "/master.idx";
                        Console.WriteLine($"Downloading {idxLink}...");
                        string content = Scraping.Common.HTTP_GET(idxLink, "", "");
                        File.WriteAllText(filePath, content);
                        Console.WriteLine($"Saved to {filePath}");
                    }
                    string disVar = "(" + year + ", " + qtr + ")";
                    Console.WriteLine("Reading MasterIdx for valid records "+ disVar);
                    List<Data> dataList = ReadMasterIdx(filePath, formMappings, lstCik, startDate, endDate,disVar);

                    foreach(Data myData in dataList)
                    {
                        //if (myData.HtmlLink == "https://www.sec.gov/Archives/edgar/data/1232524/000123252419000026/jazz2019q1doc.htm")
                        //{

                        //}
                        //else
                        //{
                        //    continue;
                        //}
                        Console.WriteLine("Reading file for match of keywords, CIK : "+myData.Cik+", Form : "+myData.FormType+", Url : "+myData.HtmlLink+" "+disVar);
                        string htmlContent = Scraping.Common.HTTP_GET(myData.HtmlLink, "", "");
                        myData.result = FindKeywordsInParagraphs(htmlContent, lstKeywords);

                        //System.Net.WebUtility.HtmlDecode(Regex.Replace(value.Trim().Replace("&nbsp;", " ").Replace("\r\n", " "), @"\s+", " ").Trim());
                        myData.matchResults = HighlightKeywords(System.Net.WebUtility.HtmlDecode( htmlContent.Replace("&nbsp;", " ")), lstKeywords, out string updatedHtml); 
                        List<string> lstTemp = new List<string>();
                        foreach(var temp in myData.result)
                        {
                            if(!lstTemp.Contains(temp.Keyword.ToLower()))
                                lstTemp.Add(temp.Keyword.ToLower());
                        }
                        if(lstTemp.Count>myData.matchResults.Count)
                        {

                        }
                        myData.highlightedHtml=updatedHtml;
                        Console.WriteLine(myData.matchResults.Count+" match(es) found!!!");

                        if(!downloadOnlyKeywordMatch)
                        {
                            string saveFinalPath = Path.Combine(outPath, myData.Cik, myData.SaveHtmlName);
                            if (!Directory.Exists(Path.GetDirectoryName(saveFinalPath)))
                                Directory.CreateDirectory(Path.GetDirectoryName(saveFinalPath));
                            File.WriteAllText(saveFinalPath,htmlContent);
                            myData.localSavePath = saveFinalPath;

                            if (myData.matchResults.Count > 0)
                            {
                                string saveFinalPathHIghlight = Path.Combine(outPath, myData.Cik, myData.SaveHtmlHighlightedName);
                                if (!Directory.Exists(Path.GetDirectoryName(saveFinalPathHIghlight)))
                                    Directory.CreateDirectory(Path.GetDirectoryName(saveFinalPathHIghlight));
                                File.WriteAllText(saveFinalPathHIghlight, myData.highlightedHtml);
                                myData.localSavePathHighlighted = saveFinalPathHIghlight;
                            }
                        }
                        //else if(myData.result.Count>0)
                        else if (myData.matchResults.Count > 0)
                        {
                            string saveFinalPath = Path.Combine(outPath, myData.Cik, myData.SaveHtmlName);
                            if (!Directory.Exists(Path.GetDirectoryName(saveFinalPath)))
                                Directory.CreateDirectory(Path.GetDirectoryName(saveFinalPath));
                            File.WriteAllText(saveFinalPath, htmlContent);
                            myData.localSavePath = saveFinalPath;

                            string saveFinalPathHIghlight = Path.Combine(outPath, myData.Cik, myData.SaveHtmlHighlightedName);
                            if (!Directory.Exists(Path.GetDirectoryName(saveFinalPathHIghlight)))
                                Directory.CreateDirectory(Path.GetDirectoryName(saveFinalPathHIghlight));
                            File.WriteAllText(saveFinalPathHIghlight, myData.highlightedHtml);
                            myData.localSavePathHighlighted = saveFinalPathHIghlight;
                        }

                        if(myData.localSavePathHighlighted==null)
                        {

                        }
                    }
                  //  continue;
                    //CIK	Date	Form 	LocalFile	KeyPhrase	Paragraph	KeyPhrase	Paragraph	KeyPhrase	Paragraph	KeyPhrase	Paragraph
                    Uri excelUri = new Uri(outFileName);
                    
                    Console.WriteLine("Saving Data to Excel "+disVar);
                    if(!File.Exists(outFileName))
                        workbook.SaveAs(outFileName);
                    foreach (Data myData in dataList)
                    {
                        if (!downloadOnlyKeywordMatch)
                        {

                            if (myData.matchResults.Count > 0)
                            {
                                foreach (var item in myData.matchResults)
                                {
                                    foreach (string val in item.Value)
                                    {
                                        string keyword = item.Key;
                                        string paragraph = val;

                                        int column = 1;
                                        ws1.Cell(curRow, column).Value = "'" + myData.Cik;
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        column++;
                                        ws1.Cell(curRow, column).Value = "'" + myData.Date.ToShortDateString();
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        column++;
                                        ws1.Cell(curRow, column).Value = "'" + myData.FormType;
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        column++;
                                        ws1.Cell(curRow, column).Value = Path.GetFileName(myData.localSavePath);
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        if (setHyperlinksLocal)
                                            ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.localSavePath);
                                        column++;

                                        if (myData.highlightedHtml != "" && myData.localSavePathHighlighted != "")
                                        {

                                            ws1.Cell(curRow, column).Value = Path.GetFileName(myData.localSavePathHighlighted);
                                            ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                            if (setHyperlinksLocal)
                                                ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.localSavePathHighlighted);
                                            column++;

                                        }
                                        else
                                        {
                                            ws1.Cell(curRow, column).Value = "";
                                            ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                            column++;
                                        }
                                        ws1.Cell(curRow, column).Value = "'" + myData.HtmlLink;
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.HtmlLink);
                                        column++;

                                        ws1.Cell(curRow, column).Value = "'" + keyword;
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        column++;
                                        ws1.Cell(curRow, column).Value = "'" + paragraph;
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        column++;
                                        curRow++; 
                                    }
                                }
                                    
                            }
                            else
                            {
                                int column = 1;
                                ws1.Cell(curRow, column).Value = "'" + myData.Cik;
                                ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                column++;
                                ws1.Cell(curRow, column).Value = "'" + myData.Date.ToShortDateString();
                                ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                column++;
                                ws1.Cell(curRow, column).Value = "'" + myData.FormType;
                                ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                column++;
                                ws1.Cell(curRow, column).Value = Path.GetFileName(myData.localSavePath);
                                ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                if (setHyperlinksLocal)
                                    ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.localSavePath);
                                column++;

                                if (myData.highlightedHtml != "" && myData.localSavePathHighlighted != "")
                                {

                                    ws1.Cell(curRow, column).Value = Path.GetFileName(myData.localSavePathHighlighted);
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    if (setHyperlinksLocal)
                                        ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.localSavePathHighlighted);
                                    column++;

                                }
                                else
                                {
                                    ws1.Cell(curRow, column).Value = "";
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    column++;
                                }
                                ws1.Cell(curRow, column).Value = "'" + myData.HtmlLink;
                                ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.HtmlLink);
                                column++;
                                curRow++;
                            }
                            
                        }
                        else if(myData.matchResults.Count>0)
                        {
                            foreach (var item in myData.matchResults)
                            {
                                foreach (string val in item.Value)
                                {
                                    string keyword = item.Key;
                                    string paragraph = val;

                                    int column = 1;
                                    ws1.Cell(curRow, column).Value = "'" + myData.Cik;
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    column++;
                                    ws1.Cell(curRow, column).Value = "'" + myData.Date.ToShortDateString();
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    column++;
                                    ws1.Cell(curRow, column).Value = "'" + myData.FormType;
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    column++;
                                    ws1.Cell(curRow, column).Value = Path.GetFileName(myData.localSavePath);
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    if (setHyperlinksLocal)
                                        ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.localSavePath);
                                    column++;

                                    if (myData.highlightedHtml != "" && myData.localSavePathHighlighted != "")
                                    {

                                        ws1.Cell(curRow, column).Value = Path.GetFileName(myData.localSavePathHighlighted);
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        if (setHyperlinksLocal)
                                            ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.localSavePathHighlighted);
                                        column++;

                                    }
                                    else
                                    {
                                        ws1.Cell(curRow, column).Value = "";
                                        ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                        column++;
                                    }
                                    ws1.Cell(curRow, column).Value = "'" + myData.HtmlLink;
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    ws1.Cell(curRow, column).Hyperlink = new XLHyperlink(myData.HtmlLink);
                                    column++;

                                    ws1.Cell(curRow, column).Value = "'" + keyword;
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    column++;
                                    ws1.Cell(curRow, column).Value = "'" + paragraph;
                                    ws1.Cell(curRow, column).DataType = XLCellValues.Text;
                                    column++;
                                    curRow++;
                                }
                            }
                        }
                    }
                    workbook.SaveAs(outFileName);
                }
            }

            Console.Clear();
            Console.WriteLine("Scraping completed, Press anykey to exit...");
            Console.ReadLine();
            Environment.Exit(0);
        }

        public static string GetRelativePath(string fromPath, string toPath)
        {
            Uri fromUri = new Uri(fromPath);
            Uri toUri = new Uri(toPath);

            if (fromUri.Scheme != toUri.Scheme) { return toPath; } // Path can't be made relative.

            Uri relativeUri = fromUri.MakeRelativeUri(toUri);
            string relativePath = Uri.UnescapeDataString(relativeUri.ToString());

            return relativePath.Replace('/', Path.DirectorySeparatorChar);
        }

        //"series of preferred"
        public static List<(string Keyword, string Paragraph)> FindKeywordsInParagraphs(string htmlContent, List<string> keywords)
        {
            var keywordMatches = new List<(string Keyword, string Paragraph)>();

            // Load HTML content
            var htmlDoc = new HtmlDocument();
            htmlDoc.LoadHtml(htmlContent);

            // Get all paragraph nodes
            //var paragraphNodes = htmlDoc.DocumentNode.SelectNodes("//p");
            var paragraphNodes = htmlDoc.DocumentNode.SelectNodes("//body/*[name()='p' or name()='div' or name()='P' or name()='DIV']");
            if (paragraphNodes == null)
            {
                return keywordMatches;
            }

            // Normalize keywords to lower case
            var normalizedKeywords = keywords.Select(k => k.ToLower()).ToList();

            // Check each paragraph
            foreach (var paragraph in paragraphNodes)
            {
                // Decode HTML entities and normalize paragraph text
                var paragraphText = HtmlEntity.DeEntitize(paragraph.InnerText)
                    .Replace("\r", " ")
                    .Replace("\n", " ")
                    .Replace("\t", " ");

                // Convert to lower case for case-insensitive search
                var normalizedParagraphText = paragraphText.ToLower();

                string tempText= CleanWhiteSpacesNew(paragraph.InnerText);

                if(normalizedParagraphText.Contains("series of preferred"))
                {

                }
                foreach (var keyword in normalizedKeywords)
                {
                    if (tempText.ToLower().Contains(keyword))
                    {
                        keywordMatches.Add((keyword, tempText.Trim()));
                    }
                }
            }

            return keywordMatches;
        }

        static Dictionary<string, List<string>> HighlightKeywords(string htmlContent, List<string> keywords, out string highlightedHtml)
        {
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(htmlContent);

            var matches = new List<(int index, string keyword)>();
            List<string> lstFoundKeywords = new List<string>();
            foreach (var keyword in keywords)
            {
                foreach (Match match in Regex.Matches(htmlContent, Regex.Escape(keyword), RegexOptions.IgnoreCase))
                {
                    matches.Add((match.Index, keyword));
                    if(!lstFoundKeywords.Contains(keyword.ToLower()))
                        lstFoundKeywords.Add(keyword.ToLower());
                }
            }

            matches = matches.OrderByDescending(m => m.index).ToList();

            foreach (var match in matches)
            {
                htmlContent = HighlightMatch(htmlContent, match.index, match.keyword);
            }

            // Reload the document with the highlighted HTML content
            doc.LoadHtml(htmlContent);

            // Recalculate matches for each keyword in the updated HTML content
            var updatedMatches = new List<(Match matchCur, string keyword)>();
            foreach (var keyword in lstFoundKeywords)
            {
                string regPattern = @"(?<m><mark id=[^>]+?>)(?<k>##key##)";
                //  foreach (Match match in Regex.Matches(htmlContent, @"(?<m><mark id=[^>]+?>)" + Regex.Escape(keyword), RegexOptions.IgnoreCase))
                foreach (Match match in Regex.Matches(htmlContent, regPattern.Replace("##key##", Regex.Escape(keyword)), RegexOptions.IgnoreCase))
                {
                    updatedMatches.Add((match, keyword));
                }
            }

            var keywordParagraphs = new Dictionary<string, List<string>>();
            foreach (var keyword in lstFoundKeywords)
            {
                var paragraphs = new List<string>();
                var keywordMatches = updatedMatches.Where(m => m.keyword.Equals(keyword, StringComparison.OrdinalIgnoreCase));

                foreach (var match in keywordMatches)
                {
                    var closestElement = FindClosestElement(doc, match.matchCur.Groups["k"].Index, match.keyword,match.matchCur);
                    if (closestElement != null)
                    {
                        string inner =cleanWhiteSpaces( closestElement.InnerText);
                        if (inner.Length > 5000)
                            inner = inner.Substring(0, 5000);
                        paragraphs.Add(inner);
                        if(closestElement.InnerText.Length>5000)
                        {

                        }
                    }
                    else
                    {
                        //handle this
                    }
                }

                keywordParagraphs[keyword] = paragraphs;
            }

            highlightedHtml = doc.DocumentNode.OuterHtml;
            return keywordParagraphs;
        }

        static string HighlightMatch(string htmlContent, int index, string keyword)
        {
            markCounter++; // increment the counter for each match
            string uniqueIndex = $"{markCounter}"; // create a unique index
            return htmlContent.Substring(0, index) + $"<mark id=\"{uniqueIndex}\">" + keyword + "</mark>" + htmlContent.Substring(index + keyword.Length);
        }
        private static int markCounter = 0;
        static HtmlNode FindClosestElement(HtmlDocument doc, int index,string keyW,Match m)
        {
            var allNodes = doc.DocumentNode.SelectNodes("//*");
            //var nodes = doc.DocumentNode.SelectNodes("//p | //div");
            var nodes = doc.DocumentNode.SelectNodes("//*[not(descendant::p or descendant::div)][self::p or self::div]");

            if (nodes == null || nodes.Count == 0)
            {
                // If no <p> or <div> tags are found, return the closest element in the document
                return FindClosestElementFromList(allNodes, index,keyW,m);
            }

            // Return the closest <p> or <div> element
            return FindClosestElementFromList(nodes, index,keyW,m);
        }

        static HtmlNode FindClosestElementFromList(HtmlNodeCollection nodes, int index,string keyW,Match m)
        {
            HtmlNode closestNode = null;
            int closestDistance = int.MaxValue;

            foreach (var node in nodes)
            {
                // int nodeIndex = node.InnerHtml.IndexOf("<mark>"+keyW, StringComparison.OrdinalIgnoreCase);
                int nodeIndex = node.InnerHtml.IndexOf(m.Groups["m"].Value + keyW, StringComparison.OrdinalIgnoreCase);
                if (nodeIndex != -1 && Math.Abs(nodeIndex - index) < closestDistance)
                {
                    closestNode = node;
                    closestDistance = Math.Abs(nodeIndex - index);
                }
            }
            if (closestDistance == int.MaxValue)
            {

            }
            return closestNode;
        }
        private static string CleanWhiteSpacesNew(string value)
        {
            // Use HtmlAgilityPack to decode HTML entities correctly
            string decodedValue = HtmlEntity.DeEntitize(value.Trim());

            // Replace &nbsp; with space and normalize white spaces
            decodedValue = Regex.Replace(decodedValue.Replace("&nbsp;", " "), @"\s+", " ").Trim();

            // Replace specific Unicode control characters with the appropriate curly quotes
            decodedValue = decodedValue.Replace("\u0091", "‘")
                                       .Replace("\u0092", "’")
                                       .Replace("\u0093", "“")
                                       .Replace("\u0094", "”")
                                       .Replace("\u0096", "–")
                                       .Replace("\u0097", "—");

            return decodedValue;
        }
        private static string cleanWhiteSpaces(string value)
        {
            return System.Net.WebUtility.HtmlDecode(Regex.Replace(value.Trim().Replace("&nbsp;", " ").Replace("\r\n", " "), @"\s+", " ").Trim());
        }
        static void ValidateDirectory(string directoryPath, string key, List<string> validationErrors)
        {
            if (string.IsNullOrWhiteSpace(directoryPath) || !Directory.Exists(directoryPath))
            {
                validationErrors.Add($"'{key}' '{directoryPath}' not found or invalid.");
            }
        }
        static string GetValue(string value, string key, List<string> validationErrors)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                validationErrors.Add($"'{key}' not found in config.ini.");
            }
            return value;
        }

        static void ValidateFilePath(string filePath, string key, List<string> validationErrors)
        {
            if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
            {
                validationErrors.Add($"'{key}' '{filePath}' not found or invalid.");
            }
        }
        static List<Data> ReadMasterIdx(string masterIdxFilePath, List<FormMapping> formMappings, List<string> lstCik, DateTime startDate, DateTime endDate,string disYearQtr)
        {
            List<Data> dataList = new List<Data>();

            // Read master.idx file
            string[] lines = File.ReadAllLines(masterIdxFilePath);
            var candidateLines = lines.Where(line =>
            {
                string cik = line.Split('|')[0].Trim();
                return lstCik.Contains(cik);
            });
            int length = candidateLines.Count();
            foreach (var line in candidateLines)
            {
                string[] parts = line.Split('|');
                if (parts.Length >= 5)
                {
                    string cik = parts[0];
                    string companyName = parts[1];
                    string formKey = parts[2];
                    string dateStr = parts[3];
                    string urlPart = parts[4];

                    // Convert date string to DateTime
                    DateTime date;
                    if (DateTime.TryParseExact(dateStr, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out date))
                    {
                        // Check if formKey matches any form mapping and if the CIK is in lstCik
                        foreach (var mapping in formMappings)
                        {
                            if (mapping.FormKey == formKey && mapping.Flag == "Y" && lstCik.Contains(cik))
                            {
                                // Filter by date range
                                if (date >= startDate && date <= endDate)
                                {
                                    Data data = new Data
                                    {
                                        Cik = cik.PadLeft(10,'0'),
                                        CompanyName = companyName,
                                        FormType = mapping.FormDisplayType,
                                        Date = date,
                                        UrlPart = urlPart,
                                        OriginalLine = line // Store the original line
                                    };
                                    Console.WriteLine("Valid record found cik : "+data.Cik+", Form : "+data.FormType+", Date : "+data.Date.ToShortDateString()+", "+data.CompanyName+", total : "+(dataList.Count+1)+" "+ disYearQtr);
                                    data.setHtmlLink();
                                    dataList.Add(data);
                                }
                            }
                        }
                    }
                }
            }
            SetHtmlPath(dataList,"out");
            return dataList;
        }
        static void SetHtmlPath(List<Data> dataList, string rootOut)
        {
            var fileNameSet = new HashSet<string>();

            foreach (var data in dataList)
            {
                string sanitizedFormType = string.Concat(data.FormType.Select(c => Path.GetInvalidFileNameChars().Contains(c) ? '_' : c));
                sanitizedFormType = sanitizedFormType.Replace(' ', '_');

                string baseFileName = $"{data.Cik}_{sanitizedFormType}_{data.Date.ToShortDateString().Replace("/", "_")}.html";
                string uniqueFileName = baseFileName;

                int index = 1;
                while (fileNameSet.Contains(uniqueFileName))
                {
                    uniqueFileName = $"{Path.GetFileNameWithoutExtension(baseFileName)}_{index++}.html";
                }

                data.SaveHtmlName = uniqueFileName;
                data.SaveHtmlHighlightedName = uniqueFileName.Replace(".html","")+"_Highlighted.html";

                fileNameSet.Add(uniqueFileName);
            }
        }
        static List<FormMapping> ReadFormMappings(string formMappingPath)
        {
            List<FormMapping> formMappings = new List<FormMapping>();

            // Read form mappings from file
            string[] lines = File.ReadAllLines(formMappingPath);
            foreach (var line in lines)
            {
                string[] parts = line.Split('|');
                if (parts.Length == 3)
                {
                    FormMapping mapping = new FormMapping
                    {
                        FormDisplayType = parts[0],
                        FormKey = parts[1],
                        Flag = parts[2]
                    };
                    formMappings.Add(mapping);
                }
            }

            return formMappings;
        }
        static List<string> GetArchiveLinks(DateTime startDate, DateTime endDate)
        {
            List<string> links = new List<string>();

            for (DateTime date = startDate; date <= endDate; date = date.AddMonths(3))
            {
                int quarter = (date.Month - 1) / 3 + 1;
                string link = $"https://www.sec.gov/Archives/edgar/full-index/{date.Year}/QTR{quarter}/";
                if (!links.Contains(link))
                {
                    links.Add(link);
                }
            }

            // Ensure the end date's quarter is included
            int endQuarter = (endDate.Month - 1) / 3 + 1;
            string endLink = $"https://www.sec.gov/Archives/edgar/full-index/{endDate.Year}/QTR{endQuarter}/";
            if (!links.Contains(endLink))
            {
                links.Add(endLink);
            }

            links.Sort((x, y) => string.Compare(x, y, StringComparison.Ordinal));
            return links;
        }

        static string GetFileNameFromLink(string link)
        {
            // Fix URL splitting issue
            link = link.Replace("://", ":/");
            string[] parts = link.Split('/');
            string year = parts[5];
            string quarter = parts[6].Replace("QTR", "Q");
            return $"{year}_{quarter}.idx";
        }
    }
    class FormMapping
    {
        public string FormDisplayType { get; set; }
        public string FormKey { get; set; }
        public string Flag { get; set; }
    }

    class Data
    {
        public string Cik { get; set; }
        public string CikOri { get; set; }
        public string CompanyName { get; set; }
        public string FormType { get; set; }
        public DateTime Date { get; set; }
        public string UrlPart { get; set; }
        public string OriginalLine { get; set; } // Store the original line from master.idx
        public string HtmlLink { get; set; }
        public string TxtLink { get; set; }

        public string SaveHtmlName { get; set; }
        public string SaveHtmlHighlightedName { get; set; }

        public string localSavePath = "";
        public string localSavePathHighlighted = "";


        public string highlightedHtml { get; set; }

        public List<(string Keyword, string Paragraph)> result;
        public Dictionary<string, List<string>> matchResults;
        public void setHtmlLink()
        {
            Match mtChk = Regex.Match(OriginalLine, @"(?<f>edgar/data/(\d+?)/)(?<l>.+)\.txt");
            if (mtChk.Success)
            {
                TxtLink = @"https://www.sec.gov/Archives/" + mtChk.Groups["f"].Value + mtChk.Groups["l"].Value.Replace("-", "") + "/" + mtChk.Groups["l"].Value + ".txt";

                // Fetch content from TxtLink
                string content = Scraping.Common.HTTP_GET(TxtLink, "", ""); // Assuming HTTP_GET fetches content

                // Extract filename for HtmlLink from content
                Match mtChkName = Regex.Match(content, @"<FILENAME>(?<f>[\w\W]+?)<DESCRIPTION>");
                if (mtChkName.Success)
                {
                    string mtChkVal = mtChkName.Groups["f"].Value.Trim();

                    // Check if mtChkVal contains tags, and refine if needed
                    if (mtChkVal.Contains("<") && mtChkVal.Contains(">"))
                    {
                        mtChkName = Regex.Match(content, @"<FILENAME>(?<f>[^<>]+?)<DESCRIPTION>");
                        if (mtChkName.Success)
                        {
                            mtChkVal = mtChkName.Groups["f"].Value.Trim();
                        }
                    }

                    HtmlLink = @"https://www.sec.gov/Archives/" + mtChk.Groups["f"].Value + mtChk.Groups["l"].Value.Replace("-", "") + "/" + mtChkVal;
                }
            }
        }
    }
}
