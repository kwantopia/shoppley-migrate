package com.shoppley.android.merchant;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.shoppley.android.api.merchant.RegisterResponse;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;
import com.shoppley.android.utils.Utils;

public class RegisterFragment extends Fragment {

	private MerchantApplication app;
	private EditText edtTxtUsn;
	private EditText edtTxtPwd;
	private EditText edtTxtPhone;
	private EditText edtTxtZipcode;
	private Button btnRegister;
	private String username = null;
	private String password = null;
	private EditText edtTxtBiz;

	public RegisterFragment() {
	}

	public RegisterFragment(String username, String password) {
		this.username = username;
		this.password = password;
	}

	private void saveCredential() {
		// Store username and password on successful login
		// We need an Editor object to make preference changes.
		// All objects are from android.context.Context
		SharedPreferences settings = getActivity().getPreferences(
				Activity.MODE_PRIVATE);
		SharedPreferences.Editor editor = settings.edit();
		editor.clear();
		editor.putString("email", edtTxtUsn.getText().toString());
		editor.putString("password", edtTxtPwd.getText().toString());

		// Commit the edits!
		editor.commit();
	}

	@Override
	public void onResume() {
		super.onResume();
		Utils.hideKeyboard(getActivity(), edtTxtUsn.getWindowToken());
		edtTxtBiz.clearFocus();

	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		app = (MerchantApplication) getActivity().getApplication();
		View v = inflater.inflate(R.layout.register, container, false);
		edtTxtBiz = (EditText) v.findViewById(R.id.edtTxtBiz);
		edtTxtUsn = (EditText) v.findViewById(R.id.edtTxtUsn);
		edtTxtPwd = (EditText) v.findViewById(R.id.edtTxtPwd);
		edtTxtPhone = (EditText) v.findViewById(R.id.edtTxtPhone);
		edtTxtZipcode = (EditText) v.findViewById(R.id.edtTxtZipcode);
		edtTxtZipcode
				.setOnEditorActionListener(new TextView.OnEditorActionListener() {
					public boolean onEditorAction(TextView v, int actionId,
							KeyEvent event) {
						if (actionId == EditorInfo.IME_ACTION_GO) {
							// Validate
							if (validateForm()) {
								// Login
								performRegister();
							}
							return true;
						}
						return false;
					}
				});
		btnRegister = (Button) v.findViewById(R.id.btnRegister);

		if (username != null) {
			edtTxtUsn.append(username);
		}
		if (password != null) {
			edtTxtPwd.append(password);
		}
		btnRegister.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				if (validateForm()) {
					performRegister();
				}
			}
		});
		return v;
	}

	protected void performRegister() {
		final ShoppleyMerchantAPI api = app.getAPI();
		final ProgressDialog registering = Utils.showLoading(getActivity(),
				"Registering...");
		BetterAsyncTask<Void, Void, RegisterResponse> task = new BetterAsyncTask<Void, Void, RegisterResponse>(
				getActivity()) {

			@Override
			protected void after(Context arg0, RegisterResponse arg1) {
				registering.hide();
				if (arg1 != null && arg1.result != null
						&& arg1.result.equals("1")) {
					saveCredential();
					Toast.makeText(getActivity(), "Succesfully registered.",
							1000).show();
					FragmentManager fm = getFragmentManager();
					fm.popBackStack();
				} else {
					if (arg1 != null && arg1.result != null) {
						Utils.createDialog(getActivity(),
								"Registration failed. " + arg1.result_msg)
								.show();
					} else {
						Utils.createDialog(getActivity(),
								"Registration failed. Please try again later.")
								.show();
					}
				}
			}

			@Override
			protected void handleError(Context arg0, Exception arg1) {
				registering.hide();
				Utils.createDialog(getActivity(),
						"Registration failed. Please try again later.").show();
			}
		};
		task.setCallable(new BetterAsyncTaskCallable<Void, Void, RegisterResponse>() {

			public RegisterResponse call(
					BetterAsyncTask<Void, Void, RegisterResponse> arg0)
					throws Exception {
				return api.merchantRegister(edtTxtBiz.getText().toString(),
						edtTxtUsn.getText().toString(), edtTxtPwd.getText()
								.toString(), edtTxtPhone.getText().toString(),
						edtTxtZipcode.getText().toString());
			}
		});
		task.execute();
	}

	private boolean validateForm() {
		if (edtTxtBiz.getText().length() == 0
				|| edtTxtPwd.getText().length() == 0
				|| edtTxtUsn.getText().length() == 0
				|| edtTxtPhone.getText().length() == 0
				|| edtTxtZipcode.getText().length() == 0) {
			// Not pass
			Utils.createDialog(
					getActivity(),
					("Business or email or password or phone or zipcode cannot be blank."))
					.show();
			return false;
		}
		return true;
	}
}
