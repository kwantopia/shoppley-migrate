//
//  RedeemViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/29/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "RedeemViewController.h"

#import "SLDataController.h"

@implementation RedeemViewController

@synthesize offerCodeField = _offerCodeField, totalPaidField = _totalPaidField;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Redeem";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_redeem.png"] tag:0] autorelease];
        
        self.tableViewStyle = UITableViewStyleGrouped;
        self.variableHeightRows = YES;
        self.tableView.scrollEnabled = NO;
        
        self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel)] autorelease];
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.offerCodeField = [[[UITextField alloc] init] autorelease];
    self.offerCodeField.delegate = self;
    self.offerCodeField.placeholder = @"Offer Code";
    self.offerCodeField.font = TTSTYLEVAR(font);
    self.offerCodeField.keyboardType = UIKeyboardTypeNumberPad;
    self.offerCodeField.autocorrectionType = UITextAutocorrectionTypeNo;
    self.offerCodeField.clearButtonMode = UITextFieldViewModeWhileEditing;
    self.offerCodeField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    self.offerCodeField.returnKeyType = UIReturnKeyNext;
    
    self.totalPaidField = [[[UITextField alloc] init] autorelease];
    self.totalPaidField.delegate = self;
    self.totalPaidField.placeholder = @"Total Paid";
    self.totalPaidField.font = TTSTYLEVAR(font);
    self.totalPaidField.keyboardType = UIKeyboardTypeDecimalPad;
    self.totalPaidField.autocorrectionType = UITextAutocorrectionTypeNo;
    self.totalPaidField.clearButtonMode = UITextFieldViewModeWhileEditing;
    self.totalPaidField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    self.totalPaidField.returnKeyType = UIReturnKeyGo;
}

- (void)createModel {
    self.dataSource = [TTListDataSource dataSourceWithObjects:self.offerCodeField, self.totalPaidField, nil];
    
    // Header
    TTStyledTextLabel* label = [[[TTStyledTextLabel alloc] initWithFrame:self.view.bounds] autorelease];
    label.font = [UIFont systemFontOfSize:14];
    label.text = [TTStyledText textFromXHTML:@"Enter customer's code to redeem." lineBreaks:NO URLs:NO];
    label.contentInset = UIEdgeInsetsMake(10, 10, 0, 10);
    label.backgroundColor = [UIColor clearColor];
    [label sizeToFit];
    label.frame = CGRectMake(0, 0, label.frame.size.width, label.frame.size.height);
    
    UIView* headerView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, label.frame.size.height)] autorelease];
    [headerView addSubview:label];
    self.tableView.tableHeaderView = headerView;
    
    // Footer
    TTButton* button = [TTButton buttonWithStyle:@"greenButton:" title:@"Redeem"];
    [button addTarget:self action:@selector(redeemClicked) forControlEvents:UIControlEventTouchUpInside];
    button.enabled = YES;
    [button sizeToFit];
    button.frame = CGRectMake(10, 10, self.view.frame.size.width - 20, button.frame.size.height);
    UIView* footerView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, button.frame.size.height + 10)] autorelease];
    [footerView addSubview:button];
    self.tableView.tableFooterView = footerView;
    
    [self.offerCodeField becomeFirstResponder];
}

- (void)clearTextFields {
    self.offerCodeField.text = nil;
    self.totalPaidField.text = nil;
}

- (void)redeemClicked {
    self.tableView.tableFooterView = NULL;
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableActivityItem itemWithText:@"Processing..."], nil];
    [self performSelectorInBackground:@selector(redeem) withObject:nil];
}

- (void)redeem {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    
    NSString* code = self.offerCodeField.text;
    
    NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
    [f setNumberStyle:NSNumberFormatterDecimalStyle];
    NSNumber* amount = [f numberFromString:self.totalPaidField.text];
    
    if (!TTIsStringWithAnyText(code) || amount == nil) {
        UIAlertView *alert = [[UIAlertView alloc]
                              initWithTitle:@""
                              message:@"Please fill both fields."
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil];
        [alert show];
        [alert release];
    } else {
        if ([[SLDataController sharedInstance] redeemCode:code amount:amount]) {
            UIAlertView *alert = [[UIAlertView alloc]
                                  initWithTitle:@""
                                  message:@"Offer redemption successful."
                                  delegate:self
                                  cancelButtonTitle:@"OK"
                                  otherButtonTitles: nil];
            [alert show];
            [alert release];
            
            [self clearTextFields];
        } else {
            UIAlertView *alert = [[UIAlertView alloc]
                                  initWithTitle:@""
                                  message:[SLDataController sharedInstance].errorString
                                  delegate:self
                                  cancelButtonTitle:@"OK"
                                  otherButtonTitles: nil];
            [alert show];
            [alert release];
        }
    }
    
    [self performSelectorOnMainThread:@selector(createModel) withObject:nil waitUntilDone:NO];
    [pool release];
}

- (void)cancel {
    [self.offerCodeField resignFirstResponder];
    [self.totalPaidField resignFirstResponder];
}

#pragma UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {    
    if (textField == self.offerCodeField) {
        [self.totalPaidField becomeFirstResponder];
    } else {
        [self redeemClicked];
    }
    return YES;
}

@end
