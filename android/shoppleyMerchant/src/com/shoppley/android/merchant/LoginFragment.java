package com.shoppley.android.merchant;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.content.DialogInterface.OnCancelListener;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnFocusChangeListener;
import android.view.View.OnTouchListener;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;

import com.shoppley.android.api.LoginResponse;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;
import com.shoppley.android.utils.Utils;

public class LoginFragment extends Fragment {
	private EditText edtTxtUsn;
	private EditText edtTxtPwd;
	private MerchantApplication app;
	protected RegisterFragment registerFragment;
	private boolean autoLogin = true;

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		app = (MerchantApplication) getActivity().getApplication();
		View v = inflater.inflate(R.layout.login, container, false);
		edtTxtUsn = (EditText) v.findViewById(R.id.edtTxtUsn);
		edtTxtPwd = (EditText) v.findViewById(R.id.edtTxtPwd);
		Button btnLogin = (Button) v.findViewById(R.id.btnLogin);
		Button btnRegister = (Button) v.findViewById(R.id.btnRegister);

		// final ScrollView scroll = (ScrollView) v.findViewById(R.id.scroll);

		// scroll.scrollTo(0, scroll.getBottom());
		// OnTouchListener touchListener = new OnTouchListener() {
		// public boolean onTouch(View v, MotionEvent event) {
		// scroll.scrollTo(0, scroll.getBottom());
		// // TODO Auto-generated method stub
		// return false;
		// }
		// };
		// OnFocusChangeListener focusListener = new OnFocusChangeListener() {
		// public void onFocusChange(View v, boolean hasFocus) {
		// scroll.scrollTo(0, scroll.getBottom());
		// }
		// };
		// edtTxtUsn.setOnTouchListener(touchListener);
		// edtTxtPwd.setOnTouchListener(touchListener);
		// edtTxtPwd.setOnFocusChangeListener(focusListener);
		btnLogin.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// Validate
				if (validateForm()) {
					// Login
					performLogin();
				}
			}
		});

		btnRegister.setOnClickListener(new OnClickListener() {

			public void onClick(View v) {
				registerFragment = new RegisterFragment(edtTxtUsn.getText()
						.toString(), edtTxtPwd.getText().toString());
				// newF.setRetainInstance(true);
				FragmentTransaction ft = getActivity()
						.getSupportFragmentManager().beginTransaction();
				ft.remove(LoginFragment.this);
				ft.add(R.id.form, registerFragment);
				ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE);
				ft.addToBackStack(null);
				ft.commit();
			}
		});
		edtTxtPwd
				.setOnEditorActionListener(new TextView.OnEditorActionListener() {
					public boolean onEditorAction(TextView v, int actionId,
							KeyEvent event) {
						if (actionId == EditorInfo.IME_ACTION_GO) {
							// Validate
							if (validateForm()) {
								// Login
								performLogin();
							}
							return true;
						}
						return false;
					}
				});

		// final FragmentManager fm = getFragmentManager();
		// fm.addOnBackStackChangedListener(new OnBackStackChangedListener() {
		// public void onBackStackChanged() {
		// if (signing != null && signing.isShowing()) {
		// signing.cancel();
		// }
		// fm.removeOnBackStackChangedListener(this);
		// }
		// });
		return v;
	}

	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);
		// Restore preferences

	};

	@Override
	public void onActivityResult(int requestCode, int resultCode, Intent data) {
		// TODO Auto-generated method stub
		autoLogin = false;
		super.onActivityResult(requestCode, resultCode, data);
	}

	@Override
	public void onResume() {
		super.onResume();
		edtTxtUsn.clearFocus();
		SharedPreferences settings = getActivity().getPreferences(
				Activity.MODE_PRIVATE);
		String email = settings.getString("email", "");
		String password = settings.getString("password", "");
		if (email.length() != 0 && password.length() != 0) {
			// Fill in username if successfully logged in
			// before
			// Fill in password if remember me is checked
			// Automatically log in if automatically log in is checked
			edtTxtUsn.setText(email);
			edtTxtPwd.setText(password);
			performLogin();
		}
	}

	private void clearCredential() {
		SharedPreferences settings = getActivity().getPreferences(
				Activity.MODE_PRIVATE);
		SharedPreferences.Editor editor = settings.edit();
		editor.clear();

		// Commit the edits!
		editor.commit();
	}

	private ProgressDialog signing = null;

	private void performLogin() {
		if (autoLogin == false) {
			autoLogin = true;
			return;
		}
		final ShoppleyMerchantAPI api = app.getAPI();
		// Show loading and perform Async login
		signing = Utils.showLoading(getActivity(),
				getString(R.string.signing_in));

		final AsyncTask<String, Void, LoginResponse> task = new AsyncTask<String, Void, LoginResponse>() {

			@Override
			protected LoginResponse doInBackground(String... params) {
				LoginResponse result = api.login(params[0], params[1]);
				// Log.d("LOGIN", result.toString());
				return result;
			}

			protected void onPostExecute(LoginResponse result) {
				signing.hide();

				if (api.isLoggedIn()) {
					saveCredential();
					Intent intent = new Intent(getActivity(),
							MerchantActivity.class);
					// Bundle paramets = new Bundle();
					// paramets.putString("YOUR_PARAM_IDENT","your_parameter_value");
					// intent.putExtras(paramets);
					startActivityForResult(intent, 0);
				} else if (api.getStatus() == ShoppleyMerchantAPI.NETWORK_ERROR) {
					Utils.createDialog(
							getActivity(),
							getString(R.string.please_check_your_network_connection))
							.show();
				} else {
					clearCredential();
					// Password did not pass
					Utils.createDialog(getActivity(),
							getString(R.string.wrong_email_or_password)).show();
				}
			};
		};
		task.execute(edtTxtUsn.getText().toString(), edtTxtPwd.getText()
				.toString());
		signing.setOnCancelListener(new OnCancelListener() {
			public void onCancel(DialogInterface arg0) {
				signing.hide();
				task.cancel(true);
			}
		});
	}

	private void saveCredential() {
		// Store username and password on successful login
		// We need an Editor object to make preference changes.
		// All objects are from android.context.Context
		SharedPreferences settings = getActivity().getPreferences(
				Activity.MODE_PRIVATE);
		SharedPreferences.Editor editor = settings.edit();
		editor.putString("email", edtTxtUsn.getText().toString());
		editor.putString("password", edtTxtPwd.getText().toString());

		// Commit the edits!
		editor.commit();
	}

	private boolean validateForm() {
		if (edtTxtPwd.getText().length() == 0
				|| edtTxtUsn.getText().length() == 0) {
			// Not pass
			Utils.createDialog(getActivity(),
					getString(R.string.email_or_password_cannot_be_blank))
					.show();
			return false;
		}
		return true;
	}

}
