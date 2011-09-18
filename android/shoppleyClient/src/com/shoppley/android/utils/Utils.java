package com.shoppley.android.utils;

import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.text.SimpleDateFormat;
import java.util.Date;

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.os.IBinder;
import android.view.View;
import android.view.inputmethod.InputMethodManager;

public class Utils {
	public static interface Callback<T> {
		public void call(T... param);
	}

	public static Dialog createConfirmDialog(Context context, String msg,
			final Callback<Void> call) {
		return new AlertDialog.Builder(context)
				.setMessage(msg)
				.setPositiveButton("Yes",
						new DialogInterface.OnClickListener() {
							public void onClick(DialogInterface dialog,
									int which) {
								call.call();
							}
						})
				.setNegativeButton("No", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						return;
					}
				}).create();
	}

	public static Dialog createDialog(Context context, String msg) {
		return new AlertDialog.Builder(context).setMessage(msg)
				.setNeutralButton("Ok", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						return;
					}
				}).create();
	}

	public static ProgressDialog showLoading(Context context, String msg) {
		ProgressDialog progressDialog = new ProgressDialog(context);
		progressDialog.setMessage(msg);
		progressDialog.setIndeterminate(true);
		progressDialog.setCancelable(true);
		progressDialog.show();
		return progressDialog;
	}

	public static Drawable loadDrawableFromURL(String url) {
		try {
			InputStream is = (InputStream) fetch(url);
			Drawable d = Drawable.createFromStream(is, "src");
			return d;
		} catch (MalformedURLException e) {
			e.printStackTrace();
			return null;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	public static Object fetch(String address) throws MalformedURLException,
			IOException {
		URL url = new URL(address);
		URLConnection connection = url.openConnection();
		connection.setUseCaches(true);
		return connection.getContent();
	}

	public static void forwardText(Context context, final String subject,
			final String message, final Callback<Intent> call) {
		final CharSequence[] items = { "SMS", "Email", "Others" };
		AlertDialog.Builder builder = new AlertDialog.Builder(context);
		builder.setTitle("Send via");
		builder.setItems(items, new DialogInterface.OnClickListener() {
			public void onClick(DialogInterface dialog, int item) {
				if (item == 0) {
					Intent intent = new Intent(Intent.ACTION_VIEW);
					intent.setType("vnd.android-dir/mms-sms");
					intent.putExtra("sms_body", message);
					call.call(intent);
				} else if (item == 1) {
					Intent emailIntent = new Intent(
							android.content.Intent.ACTION_SEND);

					emailIntent.setType("application/octet-stream");

					emailIntent.putExtra(android.content.Intent.EXTRA_SUBJECT,
							subject);

					emailIntent.putExtra(android.content.Intent.EXTRA_TEXT,
							message);

					call.call(Intent.createChooser(emailIntent,
							"Choose activity"));
				} else {
					Intent share = new Intent(Intent.ACTION_SEND);
					share.setType("text/plain");
					share.putExtra(Intent.EXTRA_TEXT, message);

					call.call(Intent.createChooser(share, "Choose activity"));
				}
			}
		}).show();
	}

	public static void hideKeyboard(Context context, IBinder windowToken) {
		InputMethodManager imm = (InputMethodManager) context
				.getSystemService(Context.INPUT_METHOD_SERVICE);
		imm.hideSoftInputFromWindow(windowToken, 0);
	}

	public static void showKeyboard(Context context, View v) {
		InputMethodManager imm = (InputMethodManager) context
				.getSystemService(Context.INPUT_METHOD_SERVICE);
		imm.showSoftInput(v, 0);
	}

	public static String secEpochToLocaleString(long sec) {
		return new Date(sec * 1000).toLocaleString();
	}

	public static String getExpiresIn(long expire_sec) {
		final long expire_ms = expire_sec * 1000;

		long nowEpoch = System.currentTimeMillis();
		String expiredTxt = "";

		long timeRemaining = expire_ms - nowEpoch;
		if (timeRemaining > 0) {
			long sec = (timeRemaining / 1000) % 60;
			long min = (timeRemaining / (1000 * 60)) % 60;
			long hours = (timeRemaining / (1000 * 60 * 60)) % 24;
			long days = (timeRemaining / (1000 * 60 * 60 * 24)) % 7;
			long weeks = (timeRemaining / (1000 * 60 * 60 * 24 * 7));
			if (weeks != 0) {
				expiredTxt = weeks + " week";
				if (days > 1) {
					expiredTxt += "s";
				}
			} else if (days != 0) {
				expiredTxt = days + " day";
				if (days > 1) {
					expiredTxt += "s";
				}
			} else if (hours != 0) {
				expiredTxt = hours + " h, " + min + " m," + sec + " s";
			} else if (min != 0) {
				expiredTxt = min + " m, " + sec + " s";
			} else if (sec != 0) {
				expiredTxt = sec + " s";
			}
		}
		return expiredTxt;
	}

	public static String getDate(long parseLong) {
		Date date = new Date(parseLong * 1000);
		SimpleDateFormat df = new SimpleDateFormat("MMMMM dd, yyyy");
		return df.format(date);
	}
	public static String getDateTime(long parseLong) {
		Date date = new Date(parseLong * 1000);
		SimpleDateFormat df = new SimpleDateFormat("MMMMM dd, yyyy 'at' h:mm a, z");
		return df.format(date);
	}
}
