package com.shoppley.android.client;

import java.util.ArrayList;
import java.util.List;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.MultiAutoCompleteTextView;
import android.widget.TextView;
import android.widget.Toast;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.higherpass.android.ContactAPI.Callback;
import com.higherpass.android.ContactAPI.ContactAPI;
import com.higherpass.android.ContactAPI.objects.Contact;
import com.higherpass.android.ContactAPI.objects.Email;
import com.higherpass.android.ContactAPI.objects.Phone;
import com.shoppley.android.api.customer.ForwardOfferResponse;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;
import com.shoppley.android.utils.Utils;

public class ForwardFragment extends Fragment {
	private String offer_code;
	private String title;

	public ForwardFragment(String offer_code, String title) {
		this.offer_code = offer_code;
		this.title = title;
	}

	public MultiAutoCompleteTextView recipients;
	private View v;

	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);

		// InputMethodManager imm = (InputMethodManager) getActivity()
		// .getSystemService(Context.INPUT_METHOD_SERVICE);
		// imm.showSoftInput(v, 1);
	}

	@Override
	public void onResume() {
		super.onResume();
		recipients.clearFocus();
		recipients.requestFocusFromTouch();
		Utils.showKeyboard(getActivity(), recipients);
	}

	private ArrayAdapter<String> ca;
	private Button btnBrowse;
	private ContactAPI api;
	private EditText edtTxtMsg;
	private Button btnSend;
	private TextView txtTitle;
	private Handler handler;

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		v = inflater.inflate(R.layout.forward, container, false);
		recipients = (MultiAutoCompleteTextView) v
				.findViewById(R.id.txtReceiver);
		btnBrowse = (Button) v.findViewById(R.id.btnBrowse);
		ShoppleyApplication app = (ShoppleyApplication) getActivity()
				.getApplication();
		api = app.getContactAPI();
		ca = app.getContactAdapter();
		// ArrayList<String> clist = new ArrayList<String>();
		// ca = new ArrayAdapter<String>(getActivity(),
		// android.R.layout.simple_dropdown_item_1line, clist);
		recipients.setAdapter(ca);
		if (api.getContactList() == null) {
			new AsyncTask<Void, Contact, Void>() {
				@Override
				protected Void doInBackground(Void... params) {
					api.newContactList(new Callback() {
						public void call(Contact contact) {
							publishProgress(contact);
						}
					});
					return null;
				}

				@Override
				protected void onProgressUpdate(Contact... contacts) {
					Contact contact = contacts[0];
					ArrayList<Phone> phones = contact.getPhone();
					if (phones != null)
						for (Phone phone : phones) {
							// Log.d("CONTACTS", contact.toString());
							ca.add(contact.getDisplayName() + " <"
									+ phone.getNumber() + ">");
						}
					ArrayList<Email> emails = contact.getEmail();
					if (emails != null)
						for (Email email : emails) {
							// Log.d("CONTACTS", contact.toString());
							ca.add(contact.getDisplayName() + " <"
									+ email.getAddress() + ">");

						}
				}
			}.execute();
		} else {
			List<Contact> contacts = api.getContactList().getContacts();
			synchronized (contacts) {
				for (Contact contact : contacts) {
					ArrayList<Phone> phones = contact.getPhone();
					if (phones != null)
						for (Phone phone : phones) {
							// Log.d("CONTACTS", contact.toString());
							ca.add(contact.getDisplayName() + " <"
									+ phone.getNumber() + ">");
						}
					ArrayList<Email> emails = contact.getEmail();
					if (emails != null)
						for (Email email : emails) {
							// Log.d("CONTACTS", contact.toString());
							ca.add(contact.getDisplayName() + " <"
									+ email.getAddress() + ">");

						}
				}
			}
		}
		recipients.setTokenizer(new MultiAutoCompleteTextView.CommaTokenizer());

		btnBrowse.setOnClickListener(new OnClickListener() {

			public void onClick(View v) {
				// TODO: Check compatibility
				// Intent intent = new Intent(Intent.ACTION_PICK,
				// People.CONTENT_URI);
				Intent intent = new Intent(Intent.ACTION_PICK, api.CONTENT_URI);
				startActivityForResult(intent, PICK_CONTACT);
			}
		});

		edtTxtMsg = (EditText) v.findViewById(R.id.edtTxtMsg);
		edtTxtMsg
				.setOnEditorActionListener(new TextView.OnEditorActionListener() {
					public boolean onEditorAction(TextView v, int actionId,
							KeyEvent event) {
						if (actionId == EditorInfo.IME_ACTION_SEND) {
							// Send
							sendMessages();
							return true;
						}
						return false;
					}
				});

		btnSend = (Button) v.findViewById(R.id.btnSend);
		btnSend.setOnClickListener(new OnClickListener() {

			public void onClick(View v) {
				sendMessages();
			}
		});

		txtTitle = (TextView) v.findViewById(R.id.txtTitle);
		txtTitle.setText(getString(R.string.forward) + " " + title);

		handler = new Handler();
		return v;
	}

	protected void sendMessages() {
		if (recipients.getText().toString().length() == 0) {
			Toast.makeText(getActivity(),
					"Please add some recipients before sending.", 500).show();
			return;
		}
		ShoppleyApplication app = (ShoppleyApplication) getActivity()
				.getApplication();
		final ShoppleyCustomerAPI api = app.getAPI();
		final ProgressDialog forwarding = Utils.showLoading(getActivity(),
				"Forwarding...");
		BetterAsyncTask<Void, Void, ForwardOfferResponse> task = new BetterAsyncTask<Void, Void, ForwardOfferResponse>(
				getActivity()) {

			@Override
			protected void after(Context arg0, ForwardOfferResponse response) {
				forwarding.hide();
				if (response != null && response.result.equals("1")) {
					Toast.makeText(getActivity(),
							getString(R.string.succesfully_forward), 500)
							.show();
					FragmentManager fm = getFragmentManager();
					Utils.hideKeyboard(getActivity(),
							edtTxtMsg.getWindowToken());
					fm.popBackStack();
				} else {
					Toast.makeText(getActivity(),
							getString(R.string.unsuccesfully_forward), 500)
							.show();

				}
			}

			@Override
			protected void handleError(Context arg0, Exception arg1) {
				forwarding.hide();
				Toast.makeText(getActivity(),
						getString(R.string.unsuccesfully_forward), 500).show();

			}

		};

		task.setCallable(new BetterAsyncTaskCallable<Void, Void, ForwardOfferResponse>() {
			public ForwardOfferResponse call(
					BetterAsyncTask<Void, Void, ForwardOfferResponse> arg0)
					throws Exception {
				ForwardOfferResponse response = api.customerForwardOffer(
						edtTxtMsg.getText().toString(), offer_code, recipients
								.getText().toString());

				return response;
			}
		});
		task.execute();

	}

	private static final int PICK_CONTACT = 1;

	@Override
	public void onActivityResult(int requestCode, int resultCode, Intent data) {
		super.onActivityResult(requestCode, resultCode, data);
		switch (requestCode) {
		case (PICK_CONTACT):
			if (resultCode == Activity.RESULT_OK) {
				Uri contactData = data.getData();
				Cursor c = getActivity().managedQuery(contactData, null, null,
						null, null);
				if (c.moveToFirst()) {
					// TODO: Check compat
					// String name = c.getString(c
					// .getColumnIndexOrThrow(People.NAME));
					String name = c.getString(c
							.getColumnIndexOrThrow(api.DISPLAY_NAME));
					String id = c.getString(c.getColumnIndexOrThrow(api._ID));
					ArrayList<Phone> phones = api.getPhoneNumbers(id);
					String target = null;
					if (phones != null && phones.size() > 0) {
						target = phones.get(0).getNumber();
					} else {
						ArrayList<Email> emails = api.getEmailAddresses(id);
						if (emails != null && emails.size() > 0) {
							target = emails.get(0).getAddress();
						}
					}
					if (target != null) {
						recipients.append(name + " <" + target + ">, ");
					} else {
						recipients.append(name);
					}
				}
			}
			break;
		}
		handler.postDelayed(new Runnable() {
			public void run() {
				recipients.clearFocus();
				recipients.requestFocus();
				Utils.showKeyboard(getActivity(), recipients);
			}
		}, 100);
	}

}
