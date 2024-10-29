using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.IO;
using HtmlAgilityPack;
using System.Web;
using System.Threading;

namespace Scraping
{
    class Common
    {
        public static HttpWebRequest request;
        public static CookieContainer cookiecontainer = new CookieContainer();
        public static HttpWebResponse response;
        public static CookieCollection cookies = new CookieCollection();
        public static string txt;
        public static string proxy="NA";
        public static string responseurl;
        public static string rzip, viewstate, eventval, html, table, opfolder, opfile, region, pageno, result;
        public static WebProxy myProxy;
        public static void clearCookies()
        {
            cookiecontainer = new CookieContainer();
            cookies = new CookieCollection();
        }

        public static string GetResponseHealth(string StrURL, string referrer, string host)
        {
            string strReturn = "";
            HttpWebRequest objRequest = null;
            IAsyncResult ar = null;
            HttpWebResponse objResponse = null;
            StreamReader objs = null;
            CookieCollection cookies = new CookieCollection();
            string source = string.Empty;

            try
            {

                objRequest = (HttpWebRequest)WebRequest.Create(StrURL);
                objRequest.CookieContainer = cookiecontainer;
                if (referrer.Length > 0) { objRequest.Referer = referrer; }
                if (host.Length > 0) { objRequest.Host = host; }
                if (!proxy.Contains("NA")) { objRequest.Proxy = new WebProxy(proxy); }
                ar = objRequest.BeginGetResponse(new AsyncCallback(GetScrapingResponse), objRequest);

                //// Wait for request to complete

                ar.AsyncWaitHandle.WaitOne(1000 * 60, true);
                if (objRequest.HaveResponse == false)
                {
                    throw new System.Exception("No Response!!!");
                }

                objResponse = (HttpWebResponse)objRequest.EndGetResponse(ar);
                responseurl = objResponse.ResponseUri.AbsoluteUri;
                foreach (Cookie c in objResponse.Cookies) { txt += c.ToString() + "\n"; }
                cookies.Add(objResponse.Cookies);
                cookiecontainer.Add(cookies);

                objs = new StreamReader(objResponse.GetResponseStream());
                strReturn = objs.ReadToEnd();
                objResponse.Close(); objs.Close();
                //http://www.cardekho.com/used-bmw+suv+cars+in+india/3
            }
            catch (System.Exception exp)
            {
                Scraping.Common.clearCookies();
                Console.WriteLine(exp.Message);
                return "";
            }
            finally
            {
                if (objResponse != null)
                    objResponse.Close();
                objRequest = null;
                ar = null;
                objResponse = null;
                objs = null;
            }
            return strReturn;
        }
        public static string GetResponse(string StrURL, string referrer, string host)
        {
            string strReturn = "";
            HttpWebRequest objRequest = null;
            IAsyncResult ar = null;
            HttpWebResponse objResponse = null;
            StreamReader objs = null;
            CookieCollection cookies = new CookieCollection();
            string source = string.Empty;

            try
            {

                objRequest = (HttpWebRequest)WebRequest.Create(StrURL);
                objRequest.CookieContainer = cookiecontainer;
                if (referrer.Length > 0) { objRequest.Referer = referrer; }
                if (host.Length > 0) { objRequest.Host = host; }
                if (!proxy.Contains("NA")) { objRequest.Proxy = new WebProxy(proxy); }
                ar = objRequest.BeginGetResponse(new AsyncCallback(GetScrapingResponse), objRequest);

                //// Wait for request to complete
                
                ar.AsyncWaitHandle.WaitOne(1000 * 60, true);
                if (objRequest.HaveResponse == false)
                {
                    throw new System.Exception("No Response!!!");
                }

                objResponse = (HttpWebResponse)objRequest.EndGetResponse(ar);
                responseurl = objResponse.ResponseUri.AbsoluteUri;
                foreach (Cookie c in objResponse.Cookies) { txt += c.ToString() + "\n"; }
                cookies.Add(objResponse.Cookies);
                cookiecontainer.Add(cookies);

                objs = new StreamReader(objResponse.GetResponseStream());
                strReturn = objs.ReadToEnd();
                objResponse.Close(); objs.Close();
                //http://www.cardekho.com/used-bmw+suv+cars+in+india/3
            }
            catch (System.Exception exp)
            {
                Scraping.Common.clearCookies();
                Console.WriteLine(exp.Message);
                return "";
            }
            finally
            {
                if (objResponse != null)
                    objResponse.Close();
                objRequest = null;
                ar = null;
                objResponse = null;
                objs = null;
            }
            return strReturn;
        }

        public static string HTTPPOST(string url, string postData, string referrer, string host)
        {
            string geturl = url;
            string source = string.Empty;

            try
            {
                ServicePointManager.Expect100Continue = true;
                ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls
                       | SecurityProtocolType.Tls11
                       | SecurityProtocolType.Tls12
                       | SecurityProtocolType.Ssl3;

                request = (HttpWebRequest)WebRequest.Create(geturl);
                request.Timeout = 20000;
                request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36";
                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }


                request.Headers.Add("authority", "provider.bcbs.com");
                request.Headers.Add("path", "/healthsparq/public/service/v2/search/point");

                request.Headers.Add("scheme", "https");
                request.Headers.Add("accept-encoding", "gzip, deflate, br");
                request.Headers.Add("accept-language", "en-US,en;q=0.9");
                

                request.Accept = "application/json, text/javascript, */*; q=0.01";
                request.ContentType = "application/x-www-form-urlencoded";

                request.Headers.Add("origin", "https://provider.bcbs.com");
                request.Headers.Add("sec-ch-ua", @""" Not A;Brand"";v=""99"", ""Chromium"";v=""100"", ""Google Chrome"";v=""100""");
                request.Headers.Add("sec-ch-ua-mobile", "?0");
                request.Headers.Add("sec-ch-ua-platform", @"""Windows""");

                request.Headers.Add("sec-fetch-dest", "empty");
                request.Headers.Add("sec-fetch-mode", "cors");
                request.Headers.Add("sec-fetch-site", "same-origin");


                request.Headers.Add("x-requested-with", "XMLHttpRequest");

                request.CookieContainer = cookiecontainer;
                //ServicePointManager.Expect100Continue = false;            
                request.Method = WebRequestMethods.Http.Post;
                request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
                request.ProtocolVersion = HttpVersion.Version11;
                request.AllowAutoRedirect = true;
                request.KeepAlive = true;

                byte[] byteArray = Encoding.ASCII.GetBytes(postData);
                request.ContentLength = byteArray.Length;
                Stream newStream = request.GetRequestStream();
                newStream.Write(byteArray, 0, byteArray.Length);
                newStream.Close();

                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
            }
            catch { source = string.Empty; }
            return source;
        }
        public static string HTTPPOST_LOGIN(string url, string postData, string referrer, string host)
        {
            string geturl = url;
            string source = string.Empty;

            try
            {
                request = (HttpWebRequest)WebRequest.Create(geturl);
                request.Timeout = 20000;
               
                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }


                request.Accept = "text/html, application/xhtml+xml, */*";
                request.Headers.Add("Accept-Language", "en-US,en;q=0.8,it-IT;q=0.5,it;q=0.3");
                //User-Agent	Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko
                request.UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko";
                //request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko";
                request.ContentType = @"application/x-www-form-urlencoded";

                request.Headers.Add("Accept-Encoding", "gzip, deflate");
                request.Headers.Add("Cache-Control", "no-cache");
                request.Headers.Add("DNT", "1");
               
                request.KeepAlive = true; 
              
                //request.Headers.Add("Origin", "http://or.occompt.com");
                //request.Headers.Add("Pragma", "no-cache");
                //request.Headers.Add("Upgrade-Insecure-Requests", "1");
                



                request.CookieContainer = cookiecontainer;            
                request.Method = WebRequestMethods.Http.Post;
                request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
                request.ProtocolVersion = HttpVersion.Version11;
                request.AllowAutoRedirect = true;
             //   request.KeepAlive = true;

                byte[] byteArray = Encoding.ASCII.GetBytes(postData);
                request.ContentLength = byteArray.Length;
                Stream newStream = request.GetRequestStream();
                newStream.Write(byteArray, 0, byteArray.Length);
                newStream.Close();

                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
            }
            catch { source = string.Empty; }
            return source;
        }
        public static string HTTPPOST_SEARCH(string url, string postData, string referrer, string host)
        {
            string geturl = url;
            string source = string.Empty;

            try
            {
                request = (HttpWebRequest)WebRequest.Create(geturl);
                request.Timeout = 20000;

                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }


                request.Accept = "text/html, application/xhtml+xml, */*";
                request.Headers.Add("Accept-Language", "en-US,en;q=0.8,it-IT;q=0.5,it;q=0.3"); 
                request.UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko"; 
                request.ContentType = @"application/x-www-form-urlencoded";

                request.Headers.Add("Accept-Encoding", "gzip, deflate");
                request.Headers.Add("DNT", "1");
                request.KeepAlive = true; 
                request.Headers.Add("Cache-Control", "no-cache"); 

                request.CookieContainer = cookiecontainer;
                request.Method = WebRequestMethods.Http.Post;
                request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
                request.ProtocolVersion = HttpVersion.Version11;
                request.AllowAutoRedirect = true;
                //   request.KeepAlive = true;

                byte[] byteArray = Encoding.ASCII.GetBytes(postData);
                request.ContentLength = byteArray.Length;
                Stream newStream = request.GetRequestStream();
                newStream.Write(byteArray, 0, byteArray.Length);
                newStream.Close();

                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
            }
            catch { source = string.Empty; }
            return source;
        }

        public static string GetResponseWithPost(string StrURL, string strPostData, string referrer, string host)
        {
            string strReturn = "";
            HttpWebRequest objRequest = null;
            ASCIIEncoding objEncoding = new ASCIIEncoding();
            Stream reqStream = null;
            HttpWebResponse objResponse = null;
            StreamReader objReader = null;
            CookieCollection cookies = new CookieCollection();

            try
            {
                objRequest = (HttpWebRequest)WebRequest.Create(StrURL);
                if (!proxy.Contains("NA")) { objRequest.Proxy = new WebProxy(proxy); }
                objRequest.Method = "POST";
                objRequest.CookieContainer = cookiecontainer;
                if (referrer.Length > 0) { objRequest.Referer = referrer; }
                if (host.Length > 0) { objRequest.Host = host; }
                byte[] objBytes = objEncoding.GetBytes(strPostData);
                objRequest.ContentLength = objBytes.Length;
                objRequest.ContentType = "application/x-www-form-urlencoded";
                reqStream = objRequest.GetRequestStream();
                reqStream.Write(objBytes, 0, objBytes.Length);

                IAsyncResult ar = objRequest.BeginGetResponse(new AsyncCallback(GetScrapingResponse), objRequest);
                //// Wait for request to complete
                ar.AsyncWaitHandle.WaitOne(1000 * 60 * 3, true);
                if (objRequest.HaveResponse == false)
                {
                    throw new System.Exception("No Response!!!");
                }
                objResponse = (HttpWebResponse)objRequest.EndGetResponse(ar);
                responseurl = objResponse.ResponseUri.AbsoluteUri;
                foreach (Cookie c in objResponse.Cookies) { txt += c.ToString() + "\n"; }
                cookies.Add(objResponse.Cookies);
                cookiecontainer.Add(cookies);

                objReader = new StreamReader(objResponse.GetResponseStream());
                strReturn = objReader.ReadToEnd();
                objResponse.Close(); objReader.Close();
            }
            catch (System.Exception exp)
            {
                return strReturn;
            }
            finally
            {
                objRequest = null;
                objEncoding = null;
                reqStream = null;
                if (objResponse != null)
                    objResponse.Close();
                objResponse = null;
                objReader = null;
            }
            return strReturn;
        }

        private static void GetScrapingResponse(IAsyncResult result)
        {

        }

        #region GET EVENT VAL and VIEW STATE AND REQUEST TOKEN VALUES
        public static string GetValueByName(string html, string name)
        {
            string value = string.Empty;

            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html);

            var hiddenNode = doc.DocumentNode.SelectSingleNode("//input[@name='" + name + "']");
            if (hiddenNode != null)
            {
                HtmlAttribute att = hiddenNode.Attributes["value"];
                if (att != null)
                {
                    value = Uri.EscapeDataString(att.Value);
                    //Console.WriteLine("View State Received");
                }
            }

            return value;
        }

        public static string escapeLargeStr(string html)
        {
            string viewS = "";
            try
            {
                viewS = Uri.EscapeDataString(html);
            }
            catch (Exception)
            {
                String value = html;
                int limit = 2000;

                StringBuilder sb = new StringBuilder();
                int loops = value.Length / limit;

                for (int i = 0; i <= loops; i++)
                {
                    if (i < loops)
                    {
                        sb.Append(Uri.EscapeDataString(value.Substring(limit * i, limit)));
                    }
                    else
                    {
                        sb.Append(Uri.EscapeDataString(value.Substring(limit * i)));
                    }
                }
                return sb.ToString();
            }
            return viewS;
        }
        public static string GetViewState_ByID(string html)
        {
            viewstate = string.Empty;
            HtmlAgilityPack.HtmlDocument doc = new HtmlAgilityPack.HtmlDocument();
            doc.LoadHtml(html);

            var hiddenNode = doc.DocumentNode.SelectSingleNode("//input[@id='__VIEWSTATE']");
            if (hiddenNode != null)
            {
                HtmlAttribute att = hiddenNode.Attributes["value"];
                if (att != null)
                {
                    try
                    {
                        viewstate = Uri.EscapeDataString(att.Value);
                    }
                    catch (Exception)
                    {
                        String value = att.Value;
                        int limit = 2000;

                        StringBuilder sb = new StringBuilder();
                        int loops = value.Length / limit;

                        for (int i = 0; i <= loops; i++)
                        {
                            if (i < loops)
                            {
                                sb.Append(Uri.EscapeDataString(value.Substring(limit * i, limit)));
                            }
                            else
                            {
                                sb.Append(Uri.EscapeDataString(value.Substring(limit * i)));
                            }
                        }
                        return sb.ToString();
                    }

                    //Console.WriteLine("View State Received");
                }
            }
            return viewstate;
        }

       

        public static string GetViewState_ByName(string html)
        {
            viewstate = string.Empty;
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html);

            var hiddenNode = doc.DocumentNode.SelectSingleNode("//input[@name='__VIEWSTATE']");
            if (hiddenNode != null)
            {
                HtmlAttribute att = hiddenNode.Attributes["value"];
                if (att != null)
                {
                    String value = att.Value;
                    int limit = 2000;

                    StringBuilder sb = new StringBuilder();
                    int loops = value.Length / limit;

                    for (int i = 0; i <= loops; i++)
                    {
                        if (i < loops)
                        {
                            sb.Append(Uri.EscapeDataString(value.Substring(limit * i, limit)));
                        }
                        else
                        {
                            sb.Append(Uri.EscapeDataString(value.Substring(limit * i)));
                        }
                    }
                    //viewstate = Uri.EscapeDataString(att.Value);
                    viewstate = sb.ToString();
                    //Console.WriteLine("View State Received");
                }
            }
            return viewstate;
        }

        
        public static string getJsonPost(string url, string jsonVal)
        {
            try
            {
                var httpWebRequest = (HttpWebRequest)WebRequest.Create(url);
                httpWebRequest.ContentType = "text/json";
                httpWebRequest.Method = "POST";

                using (var streamWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
                {
                    //string json = "{\"user\":\"test\"," +
                    //              "\"password\":\"bla\"}";
                    string json = jsonVal;
                    streamWriter.Write(json);
                    streamWriter.Flush();
                    streamWriter.Close();
                }

                var httpResponse = (HttpWebResponse)httpWebRequest.GetResponse();
                using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
                {
                    var result = streamReader.ReadToEnd();
                    return result.ToString();
                }
            }
            catch (Exception)
            {

                return "";
            }

        }
        public static string getJsonPostNew(string url, string jsonParams, string referrer,string host)
        {
            string source = string.Empty;
            try
            {
                request = (HttpWebRequest)WebRequest.Create(url);
                request.Timeout = 20000;
                request.ContentType = "application/json;charset=UTF-8";

                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }

                request.Method = "POST";
                request.KeepAlive = true;
                request.ContentLength = 49;
                request.Accept = @"application/json, text/plain, */*";
                request.UserAgent = @"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36";

                request.Headers.Add("Accept-Language", "en-US,en;q=0.8");
                request.Headers.Add("Accept-Encoding", "gzip, deflate");
                request.CookieContainer = cookiecontainer;

                byte[] byteArray = Encoding.ASCII.GetBytes(jsonParams);
                request.ContentLength = byteArray.Length;
                Stream newStream = request.GetRequestStream();
                newStream.Write(byteArray, 0, byteArray.Length);
                newStream.Close();

                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                //Console.WriteLine(txt);
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
                
            }
            catch (Exception)
            {

                source= "";
            }
            return source;
        }
        public static string HTTP_GETHealth(string url, string referrer, string host)
        {
            string source = string.Empty;
            try
            {
                request.Headers.Add("authority", "www.healthgrades.com");
                request.Headers.Add("method", "GET");
                request.Headers.Add("scheme", "https");
                request.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";
                request.Headers.Add("accept-encoding", "gzip, deflate, sdch, br");

                request.Headers.Add("accept-language", "en-us,en;q=0.5;q=0.8,sv;q=0.6");
                request.Headers.Add("cache-control", "no-cache");


                request.Headers.Add("pragma", "no-cache");
                request.Headers.Add("upgrade-insecure-requests", "1");

                request = (HttpWebRequest)WebRequest.Create(url);
                request.Timeout = 20000;
                request.UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36";
                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }
               
                //request.ContentType = "application/x-www-form-urlencoded; charset=UTF-8";
                //request.Headers.Add("Accept-Language", "en-us,en;q=0.5;q=0.8,sv;q=0.6");
               
                //request.Headers.Add("X-Requested-With", "XMLHttpRequest");
                request.Method = WebRequestMethods.Http.Get;
                request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
                request.KeepAlive = true;
                request.AllowAutoRedirect = true;
                request.CookieContainer = cookiecontainer;
                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                //Console.WriteLine(txt);
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
            }
            catch { source = string.Empty; }
            return source;
        }
        public static string HTTP_GET(string url, string referrer, string host)
        {

            string source = string.Empty;
            try
            {
                Scraping.Common.clearCookies();

                Thread.Sleep(500);

                ServicePointManager.Expect100Continue = true;
                ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls
                       | SecurityProtocolType.Tls11
                       | SecurityProtocolType.Tls12
                       | SecurityProtocolType.Ssl3;
                request = (HttpWebRequest)WebRequest.Create(url);
                //  request.Proxy = myProxy;
                request.Timeout = 20000;
                //Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
                request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36";
                //request.UserAgent = @"Mozilla/5.0";
                request.Headers.Add("authority", "www.sec.gov");
                request.Headers.Add("scheme", "https");
                request.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7";
                request.Headers.Add("cache-control", "no-cache");

                request.Headers.Add("Accept-Encoding", "gzip, deflate, br, zstd");
                request.Headers.Add("Accept-Language", "en-US,en;q=0.9");

                request.Headers.Add("Sec-Ch-Ua", @"""Chromium"";v=""122"", ""Not(A:Brand"";v=""24"", ""Google Chrome"";v=""122""");
                request.Headers.Add("Sec-Ch-Ua-Mobile", "?0");
                request.Headers.Add("Sec-Ch-Ua-Platform", @"""Windows""");
                request.Headers.Add("Sec-Fetch-Dest", "document");
                request.Headers.Add("Sec-Fetch-Mode", "navigate");
                request.Headers.Add("Sec-Fetch-Site", "node");
                request.Headers.Add("Sec-Fetch-User", "?1");
                request.Headers.Add("Upgrade-Insecure-Requests", "1");

                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }

                request.Method = WebRequestMethods.Http.Get;
                request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
                request.KeepAlive = true;
                request.AllowAutoRedirect = true;
                request.CookieContainer = cookiecontainer;
                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                //Console.WriteLine(txt);
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
            }
            catch (Exception ex)
            {
                try
                {
                    Console.WriteLine("Error : " + ex.Message + ", Wait for 5 seconds");
                    source = String.Empty;
                    Thread.Sleep(5000);
                    GC.Collect();
                    clearCookies();

                    ServicePointManager.Expect100Continue = true;
                    ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls
                           | SecurityProtocolType.Tls11
                           | SecurityProtocolType.Tls12
                           | SecurityProtocolType.Ssl3;
                    request = (HttpWebRequest)WebRequest.Create(url);
                    //  request.Proxy = myProxy;
                    request.Timeout = 20000;
                    //Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
                    //request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36";
                    request.UserAgent = @"Mozilla/5.0";
                    request.Headers.Add("authority", "www.sec.gov");
                    request.Headers.Add("scheme", "https");
                    request.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7";
                    request.Headers.Add("cache-control", "no-cache");

                    request.Headers.Add("Accept-Encoding", "gzip, deflate, br, zstd");
                    request.Headers.Add("Accept-Language", "en-US,en;q=0.9");

                    request.Headers.Add("Sec-Ch-Ua", @"""Chromium"";v=""122"", ""Not(A:Brand"";v=""24"", ""Google Chrome"";v=""122""");
                    request.Headers.Add("Sec-Ch-Ua-Mobile", "?0");
                    request.Headers.Add("Sec-Ch-Ua-Platform", @"""Windows""");
                    request.Headers.Add("Sec-Fetch-Dest", "document");
                    request.Headers.Add("Sec-Fetch-Mode", "navigate");
                    request.Headers.Add("Sec-Fetch-Site", "node");
                    request.Headers.Add("Sec-Fetch-User", "?1");
                    request.Headers.Add("Upgrade-Insecure-Requests", "1");

                    if (referrer.Length > 0) { request.Referer = referrer; }
                    if (host.Length > 0) { request.Host = host; }
                    if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }

                    request.Method = WebRequestMethods.Http.Get;
                    request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
                    request.KeepAlive = true;
                    request.AllowAutoRedirect = true;
                    request.CookieContainer = cookiecontainer;
                    response = (HttpWebResponse)request.GetResponse();
                    responseurl = response.ResponseUri.AbsoluteUri;
                    string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                    foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                    //Console.WriteLine(txt);
                    cookiecontainer.Add(response.Cookies);

                    StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                    source = searchsrc.ReadToEnd();
                    response.Close(); searchsrc.Close();
                }
                catch (Exception dd)
                {
                    if (ex.Message.Contains("404"))
                        source = "Error : 404";
                    else if (ex.Message.Contains("403"))
                        source = "Error : 403";
                    else if (ex.Message.ToLower().Contains("timed out"))
                        source = "Error : 403";
                    else
                        source = "Error :";
                }
            }
            return source;
        }
        public static string HTTP_GET_LOGIN(string url, string referrer, string host)
        {
            string source = string.Empty;
            try
            {
                request = (HttpWebRequest)WebRequest.Create(url);
                request.Timeout = 20000;

                request.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8";
                request.Headers.Add("Accept-Encoding", "gzip, deflate");
                request.Headers.Add("Accept-Language", "en-US,en;q=0.8");
                request.Headers.Add("Cache-Control", "no-cache");
                request.KeepAlive = true;
                request.ContentType = @"application/x-www-form-urlencoded";
                request.Headers.Add("Origin", "http://or.occompt.com");
                request.Headers.Add("Pragma", "no-cache");
                request.Headers.Add("Upgrade-Insecure-Requests", "1");
                request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36";



                if (referrer.Length > 0) { request.Referer = referrer; }
                if (host.Length > 0) { request.Host = host; }
                if (!proxy.Contains("NA")) { request.Proxy = new WebProxy(proxy); }  
                request.Method = WebRequestMethods.Http.Get;
                request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;
               
                request.AllowAutoRedirect = true;
                request.CookieContainer = cookiecontainer;
                response = (HttpWebResponse)request.GetResponse();
                responseurl = response.ResponseUri.AbsoluteUri;
                string txt = "Cookies Count=" + response.Cookies.Count.ToString() + "\n";
                foreach (Cookie c in response.Cookies) { txt += c.ToString() + "\n"; }
                //Console.WriteLine(txt);
                cookiecontainer.Add(response.Cookies);

                StreamReader searchsrc = new StreamReader(response.GetResponseStream());
                source = searchsrc.ReadToEnd();
                response.Close(); searchsrc.Close();
            }
            catch { source = string.Empty; }
            return source;
        }
        public static string GetEventVal(string html)
        {
            eventval = string.Empty;
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html);

            var hiddenNode = doc.DocumentNode.SelectSingleNode("//input[@id='__EVENTVALIDATION']");
            if (hiddenNode != null)
            {
                HtmlAttribute att = hiddenNode.Attributes["value"];
                if (att != null)
                {
                    eventval = Uri.EscapeDataString(att.Value);
                    //Console.WriteLine("Event Validation Received");
                }
            }
            return eventval;
        }

        public static string GetTagValue_ByID(string html, string tagname)
        {
            string tagvalue = string.Empty;
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html);

            var hiddenNode = doc.DocumentNode.SelectSingleNode("//input[@id='" + tagname + "']");
            if (hiddenNode != null)
            {
                HtmlAttribute att = hiddenNode.Attributes["value"];
                if (att != null)
                {
                    tagvalue = Uri.EscapeDataString(att.Value);
                    //Console.WriteLine("View State Received");
                }
            }
            return tagvalue;
        }
        //public static LatLng GetLatLng(string zip)
        //{
        //    string json = string.Empty; while (json.Length == 0) { json = Scraping.Common.GetResponse("http://maps.googleapis.com/maps/api/geocode/json?address=&components=postal_code:" + zip + "&sensor=false", string.Empty, string.Empty); }
        //    LatLng latLng = new LatLng();
        //    try
        //    {
        //        dynamic jsonResponce = Newtonsoft.Json.JsonConvert.DeserializeObject(json);
        //        latLng.lat = jsonResponce.results[0].geometry.location.lat;
        //        latLng.lng = jsonResponce.results[0].geometry.location.lng;

        //        latLng.city = jsonResponce.results[0].address_components[1].long_name;

        //        return latLng;
        //    }
        //    catch (Exception ex)
        //    {
        //        return null;
        //    }
        //}

        public static string GetRequestToken_ByName(string html)
        {
            viewstate = string.Empty;
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(html);

            var hiddenNode = doc.DocumentNode.SelectSingleNode("//input[@name='__RequestVerificationToken']");
            if (hiddenNode != null)
            {
                HtmlAttribute att = hiddenNode.Attributes["value"];
                if (att != null)
                {
                    viewstate = Uri.EscapeDataString(att.Value);
                    //Console.WriteLine("View State Received");
                }
            }
            return viewstate;
        }
        #endregion

        #region InfiBOT parsing functions
        public static bool isnumeric(string text)
        {
            bool flag;
            double num;
            if (double.TryParse(text, out num))
            {
                flag = true;
            }
            else
            {
                flag = false;
            }
            return flag;
        }

        public static string ParseRight(string main, string substring)
        {
            if (main.Contains(substring) == true)
            {
                result = main.Substring(main.IndexOf(substring) + substring.Length);
                result = result.Trim();
            }
            else
            {
                result = main;
            }
            return result;
        }

        public static string ParseLeft(string main, string substring)
        {
            if (main.Contains(substring) == true)
            {
                result = main.Substring(0, main.IndexOf(substring));
                result = result.Trim();
            }
            else
            {
                result = main;
            }
            return result;
        }

        public static string ParseRightRev(string main, string substring)
        {
            if (main.Contains(substring) == true)
            {
                result = main.Substring(main.LastIndexOf(substring), main.Length - main.LastIndexOf(substring));
                result = result.Substring(result.IndexOf(substring) + substring.Length);
                result = result.Trim();
            }
            else
            {
                result = main;
            }
            return result;
        }

        public static string ParseLeftRev(string main, string substring)
        {
            if (main.Contains(substring) == true)
            {
                result = main.Substring(0, main.LastIndexOf(substring));
                result = result.Trim();
            }
            else
            {
                result = main;
            }
            return result;
        }

        public static string GetDetail(string main, string before, string after)
        {
            if (main.Contains(before) == true && main.Contains(after) == true)
            {
                main = ParseRight(main, before);
                main = ParseLeft(main, after);
                main = RemoveAllTags(main);
                result = FindnReplace(main, "");
            }
            else
            {
                result = string.Empty;
            }
            return result;
        }

        public static string RemoveAllTags(string main)
        {
            main = System.Text.RegularExpressions.Regex.Replace(main, @"<(.|\n)*?>", string.Empty);
            return FindnReplace(main, "");
        }

        public static string FindnReplace(string main, string substring)
        {
            try
            {
                main = main.Replace("&amp;", "&");
                main = main.Replace("&nbsp;", "");
                main = main.Replace("&#160;", string.Empty);
                main = main.Replace("\n", string.Empty);
                main = main.Replace("\r", string.Empty);
                main = main.Replace("\t", string.Empty);
                main = main.Replace("\\u0026", "&");
                while (main.Contains("  ")) { main = main.Replace("  ", " "); }
                //main = Regex.Replace(main, @"[^\u0000-\u007F]", "");
                //main = Regex.Replace(main, "[éèëêð]", "e");
                //main = Regex.Replace(main, "[ÉÈËÊ]", "E");
                //main = Regex.Replace(main, "[àâä]", "a");
                //main = Regex.Replace(main, "[ÀÁÂÃÄÅ]", "A");
                //main = Regex.Replace(main, "[àáâãäå]", "a");
                //main = Regex.Replace(main, "[ÙÚÛÜ]", "U");
                //main = Regex.Replace(main, "[ùúûüµ]", "u");
                //main = Regex.Replace(main, "[òóôõöø]", "o");
                //main = Regex.Replace(main, "[ÒÓÔÕÖØ]", "O");
                //main = Regex.Replace(main, "[ìíîï]", "i");
                //main = Regex.Replace(main, "[ÌÍÎÏ]", "I");
                //main = Regex.Replace(main, "[š]", "s");
                //main = Regex.Replace(main, "[Š]", "S");
                //main = Regex.Replace(main, "[ñ]", "n");
                //main = Regex.Replace(main, "[Ñ]", "N");
                //main = Regex.Replace(main, "[ç]", "c");
                //main = Regex.Replace(main, "[Ç]", "C");
                //main = Regex.Replace(main, "[ÿ]", "y");
                //main = Regex.Replace(main, "[Ÿ]", "Y");
                //main = Regex.Replace(main, "[ž]", "z");
                //main = Regex.Replace(main, "[Ž]", "Z");
                //main = Regex.Replace(main, "[Ð]", "D");
                //main = Regex.Replace(main, "[œ]", "oe");
                //main = Regex.Replace(main, "[Œ]", "Oe");
                //main = Regex.Replace(main, "[«»\u201C\u201D\u201E\u201F\u2033\u2036]", "\"");
                //main = Regex.Replace(main, "[\u2026]", "...");
                result = main;
            }
            catch
            {
            }
            return result;
        }
        #endregion
        public static List<string> GetZipList(string zipCode)
        {
            Console.Write("Getting Zip list for " + zipCode);
            List<string> lst = new List<string>();
            string zipHtml = string.Empty; while (zipHtml.Length == 0) { zipHtml = GetResponse("http://www.unitedstateszipcodes.org/" + zipCode + "/", "", ""); }
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(zipHtml);
            HtmlNodeCollection colTrs = doc.DocumentNode.SelectNodes("//table[@class='lined']/tr");
            if (colTrs != null)
            {
                foreach (HtmlNode ndTr in colTrs)
                {
                    if (ndTr.Attributes["class"] != null && ndTr.Attributes["class"].Value == "header_row")
                        continue;

                    HtmlNode ndA = ndTr.SelectSingleNode("./td[1]/a");
                    if (ndA != null)
                        lst.Add(ndA.InnerText.PadLeft(5,'0'));
                }
            }
            Console.Write("\rGetting Zip list for " + zipCode + ". " + lst.Count + " zips found.");
            Console.WriteLine("");
            return lst;
        }
        public static string TrimStart(string target, string trimString)
        {
            string result = target;
            while (result.StartsWith(trimString))
            {
                result = result.Substring(trimString.Length);
            }

            return result.Trim();
        }
        public static string TrimEnd(string target, string trimString)
        {
            string result = target;
            while (result.EndsWith(trimString))
            {
                result = result.Substring(0, result.Length - trimString.Length);
            }

            return result.Trim();
        }


    }
    public class LatLng
    {
        public string lat;
        public string lng;
        public string city;
    }
}
