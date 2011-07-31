package com.shoppley.android.client;

import android.app.Dialog;
import android.content.Intent;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentTransaction;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.ImageView;

public class LoginActivity extends FragmentActivity {
	/**
	 * Simple class for storing important data across config changes
	 */
	// private class SavedState {
	// // Your other important fields here
	// }

	// private static final int DIALOG_INVALID_ID = 0;
	//
	// private static final int DIALOG_NETWORK_ID = 3;
	//
	// private static final int DIALOG_SIGNING_ID = 2;
	//
	// private static final int DIALOG_WRONG_ID = 1;

	// private void showKeyboard(Activity act, EditText t) {
	// InputMethodManager imm = (InputMethodManager) act
	// .getSystemService(Context.INPUT_METHOD_SERVICE);
	// imm.showSoftInput(t, 1);
	// }

	// @Override
	// protected void onCreate(Bundle savedInstanceState) {
	// // TODO Auto-generated method stub
	// super.onCreate(savedInstanceState);
	// setContentView(R.layout.forward);
	// }
	/**
	 * Simple Dialog used to show the splash screen
	 */
	protected Dialog mSplashDialog;

	private LoginFragment loginFragment;

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		// SavedState data = (SavedState) getLastNonConfigurationInstance();
		// if (data != null) {
		// Show splash screen if still loading
		// setContentView(R.layout.login_main);

		// Rebuild your UI with your saved state here

		// } else {
		setContentView(R.layout.login_main);

		showSplashScreen();

		new AsyncTask<Void, Void, Void>() {

			@Override
			protected Void doInBackground(Void... params) {
				// Do your heavy loading here adn saved in data
				return null;
			}

			@Override
			protected void onPostExecute(Void result) {
				super.onPostExecute(result);
				removeSplashScreen();
			}

		}.execute();
		// }

		ImageView logo = (ImageView) findViewById(R.id.imgLogo);
		logo.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				Intent web = new Intent(Intent.ACTION_VIEW).setData(Uri
						.parse("http://www.shoppley.com"));
				startActivity(web);
			}
		});

		loginFragment = new LoginFragment();
		// newF.setRetainInstance(true);
		FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
		ft.add(R.id.form, loginFragment);
		ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
		// ft.addToBackStack(null);
		ft.commit();
	}

	//
	// @Override
	// protected Dialog onCreateDialog(int id) {
	// switch (id) {
	// case DIALOG_INVALID_ID: {
	// return Utils.createDialog(this,
	// getString(R.string.email_or_password_cannot_be_blank));
	// }
	// case DIALOG_WRONG_ID: {
	// return Utils.createDialog(this,
	// getString(R.string.wrong_email_or_password));
	// }
	// case DIALOG_SIGNING_ID: {
	// progressDialog = new ProgressDialog(this);
	// progressDialog.setMessage(getString(R.string.signing_in));
	// progressDialog.setIndeterminate(true);
	// progressDialog.setCancelable(true);
	// return progressDialog;
	// }
	// case DIALOG_NETWORK_ID: {
	// return Utils.createDialog(this,
	// getString(R.string.please_check_your_network_connection));
	// }
	// }
	// return super.onCreateDialog(id);
	// }

	@Override
	protected void onResume() {
		super.onResume();
		// Focus at username
		// Every time we return to this page also bring up the keyboard.
		// Bring up keyboard at start
		// final EditText edtTxtUsn = (EditText) findViewById(R.id.edtTxtUsn);
		// new Handler().postDelayed(new Runnable() {
		// public void run() {
		// // TODO Auto-generated method stub
		// showKeyboard(LoginActivity.this, edtTxtUsn);
		// }
		// }, 1000);
	}

	// @Override
	// public Object onRetainNonConfigurationInstance() {
	// SavedState data = new SavedState();
	// // Save your important data here
	//
	// return data;
	// }

	@Override
	public void setContentView(int layoutResID) {
		// TODO Auto-generated method stub
		super.setContentView(layoutResID);

		// TextView tv = (TextView) findViewById(R.id.txtVwLnk);
		// tv.setMovementMethod(LinkMovementMethod.getInstance());
		// tv.setText(Html
		// .fromHtml("<a href=\"http://www.shoppley.com\">http://www.shoppley.com</a>"));
	}

	/**
	 * Shows the splash screen over the full Activity
	 */
	protected void showSplashScreen() {
		mSplashDialog = new Dialog(this, R.style.SplashScreen);
		mSplashDialog.setContentView(R.layout.splash_screen);
		mSplashDialog.setCancelable(false);
		mSplashDialog.show();

		// Set Runnable to remove splash screen just in case
		final Handler handler = new Handler();
		handler.postDelayed(new Runnable() {
			public void run() {
				removeSplashScreen();
			}
		}, 1000);
	}

	/**
	 * Removes the Dialog that displays the splash screen
	 */
	protected void removeSplashScreen() {
		if (mSplashDialog != null) {
			mSplashDialog.dismiss();
			mSplashDialog = null;
		}
	}

}