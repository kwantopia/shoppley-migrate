//
//  OfferFeedbackViewController.m
//  shoppleyClient
//
//  Created by yod on 6/19/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferFeedbackViewController.h"

#import "SLDataController.h"

@implementation OfferFeedbackViewController

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [self init])) {
        _offer = [[query objectForKey:@"offer"] retain];
    }
    return self;
}

- (id)init {
    if ((self = [super init])) {
        self.tableViewStyle = UITableViewStyleGrouped;
        self.autoresizesForKeyboard = YES;
        self.variableHeightRows = YES;
        
        self.title = @"Feedback";
        
        _doneButton = [[UIBarButtonItem alloc] initWithTitle:@"Done" style:UIBarButtonItemStyleDone target:self action:@selector(submit)];
        _cancelButton = [[UIBarButtonItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(dismiss)];
        
        self.navigationItem.rightBarButtonItem = _doneButton;
        self.navigationItem.leftBarButtonItem = _cancelButton;
        
        _commentTextView = [[UITextView alloc] init];
        _commentTextView.text = @"";
        _commentTextView.font = TTSTYLEVAR(font);
        
        self.dataSource = [TTListDataSource dataSourceWithObjects:_commentTextView, nil];
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    TT_RELEASE_SAFELY(_commentTextView);
    TT_RELEASE_SAFELY(_doneButton);
    TT_RELEASE_SAFELY(_cancelButton);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.tableView.scrollEnabled = NO;
    [_commentTextView becomeFirstResponder];
}

- (void)dismiss {
    if (_commentTextView.text.length > 0) {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Cancel" message:@"Do you want to discard your change?" delegate:self cancelButtonTitle:@"NO" otherButtonTitles:@"YES", nil] autorelease];
        [alert show];
    } else {
        [self.navigationController popViewControllerAnimated:YES];
    }
}

- (void)submit {
    _doneButton.enabled = NO;
    _cancelButton.enabled = NO;
    _commentTextView.editable = NO;
    
    if ([[SLDataController sharedInstance] sendFeedBack:_commentTextView.text offerCodeId:_offer.offerCodeId]) {
        [self.navigationController popViewControllerAnimated:YES];
    } else {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Connection Error" message:@"Please try again later." delegate:self cancelButtonTitle:@"OK" otherButtonTitles: nil] autorelease];
        [alert show];
    }
}

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (buttonIndex == 0) {
        _doneButton.enabled = YES;
        _cancelButton.enabled = YES;
        _commentTextView.editable = YES;
    } else if (buttonIndex == 1) {
        // dismiss
        [self.navigationController popViewControllerAnimated:YES];
    }
}

@end
