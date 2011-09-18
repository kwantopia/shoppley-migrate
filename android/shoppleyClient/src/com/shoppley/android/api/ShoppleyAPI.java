package com.shoppley.android.api;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.ParseException;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URLEncodedUtils;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.protocol.HTTP;
import org.apache.http.util.EntityUtils;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

import com.google.gson.Gson;

public class ShoppleyAPI {

//	public static final String BASEURL = "http://webuy-dev.mit.edu";
//	public static final String BASEURL = "http://dummyshoppley.appspot.com";
	public static final String BASEURL = "http://www.shoppley.com";
	public static int NETWORK_ERROR = -1;
	public static int NORMAL = 0;
	protected static final String VERSION = "1";
	protected Header[] cookies = null;
	private String email = null;

	protected Gson gson = new Gson();
	private boolean loggedIn = false;

	private int status = NORMAL;

	public LoginResponse login(String usn, String pwd) {
		setLoggedIn(false);
		JSONObject obj = new JSONObject();
		try {
			obj.put("email", usn);
			obj.put("password", pwd);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest("/m/login/", obj);
			cookies = response.getHeaders("set-cookie");
			Log.d("Cookies", cookies.toString());
			LoginResponse loginResponse = null;
			if (cookies != null & cookies.length > 0) {
				if ((loginResponse = gson.fromJson(
						EntityUtils.toString(response.getEntity()),
						LoginResponse.class)).result.equals("1")) {
					setLoggedIn(true);
					email = usn;
				}
			}
			return loginResponse;
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			status = NETWORK_ERROR;
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
			status = NETWORK_ERROR;
		}
		return null;
	}

	public LogoutResponse logout() {
		setLoggedIn(false);
		JSONObject obj = new JSONObject();
		try {
			HttpResponse response = httpGetRequest("/m/logout/", obj);
			cookies = null;
			setLoggedIn(false);
			return gson.fromJson(EntityUtils.toString(response.getEntity()),
					LogoutResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public String getCustomerEmail() {
		return email;
	}

	public int getStatus() {
		return status;
	}

	protected HttpResponse httpGetRequest(String url, JSONObject data) {
		url = BASEURL + url;
		try {
			data.put("v", VERSION);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
		}

		if (!url.endsWith("?"))
			url += "?";

		// Create a new HttpClient and Post Header
		HttpClient httpclient = new DefaultHttpClient();
		HttpGet httpget = new HttpGet(url
				+ URLEncodedUtils.format(JSONObjectToNameValuePairList(data),
						"utf-8"));

		try {
			// Set cookies
			if (cookies != null && cookies.length > 0) {
				httpget.setHeader("Cookie", cookies[0].getValue());
			}

			// Execute HTTP Post Request
			return httpclient.execute(httpget);
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
		} catch (IOException e) {
			// TODO Auto-generated catch block
		}
		return null;
	}
	protected HttpResponse httpPostRequestNoCookies(String url, JSONObject data) {
		url = BASEURL + url;
		try {
			data.put("v", VERSION);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// Create a new HttpClient and Post Header
		HttpClient httpclient = new DefaultHttpClient();
		HttpPost httppost = new HttpPost(url);

		try {
			// Add data
			UrlEncodedFormEntity ent = new UrlEncodedFormEntity(
					JSONObjectToNameValuePairList(data), HTTP.UTF_8);
			httppost.setEntity(ent);

			// Execute HTTP Post Request
			return httpclient.execute(httppost);

		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
		} catch (IOException e) {
			// TODO Auto-generated catch block
		}
		return null;
	}
	protected HttpResponse httpPostRequest(String url, JSONObject data) {
		url = BASEURL + url;
		try {
			data.put("v", VERSION);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// Create a new HttpClient and Post Header
		HttpClient httpclient = new DefaultHttpClient();
		HttpPost httppost = new HttpPost(url);

		try {
			// Add data
			UrlEncodedFormEntity ent = new UrlEncodedFormEntity(
					JSONObjectToNameValuePairList(data), HTTP.UTF_8);
			httppost.setEntity(ent);

			// Set cookies
			if (cookies != null && cookies.length > 0) {
				httppost.setHeader("Cookie", cookies[0].getValue());
			}

			// Execute HTTP Post Request
			return httpclient.execute(httppost);

		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
		} catch (IOException e) {
			// TODO Auto-generated catch block
		}
		return null;
	}

	public boolean isLoggedIn() {
		return loggedIn;
	}

	protected List<NameValuePair> JSONObjectToNameValuePairList(JSONObject data) {
		List<NameValuePair> params = new ArrayList<NameValuePair>();
		@SuppressWarnings("unchecked")
		Iterator<String> keys = data.keys();
		while (keys.hasNext()) {
			String key = keys.next();
			try {
				params.add(new BasicNameValuePair(key, data.getString(key)));
			} catch (JSONException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		return params;
	}

	private void setLoggedIn(boolean loggedIn) {
		this.loggedIn = loggedIn;
	}

}
