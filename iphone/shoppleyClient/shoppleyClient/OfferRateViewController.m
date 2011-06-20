//
//  OfferRateViewController.m
//  shoppleyClient
//
//  Created by yod on 6/20/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferRateViewController.h"

#import "SLDataController.h"

@implementation OfferRateViewController

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [self init])) {
        _offer = [[query objectForKey:@"offer"] retain];
    }
    return self;
}

- (id)init {
    if ((self = [super init])) {
        self.tableViewStyle = UITableViewStyleGrouped;
        
        self.title = @"Rating";
        
        _doneButton = [[UIBarButtonItem alloc] initWithTitle:@"Done" style:UIBarButtonItemStyleDone target:self action:@selector(submit)];
        _cancelButton = [[UIBarButtonItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(dismiss)];
        
        self.navigationItem.rightBarButtonItem = _doneButton;
        self.navigationItem.leftBarButtonItem = _cancelButton;
        
        NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i <= 5; i++) {
            [items addObject:[TTTableTextItem itemWithText:[NSString stringWithFormat:@"%d", i]]];
        }
        self.dataSource = [TTListDataSource dataSourceWithItems:items];
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    TT_RELEASE_SAFELY(_cancelButton);
    TT_RELEASE_SAFELY(_doneButton);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.tableView.scrollEnabled = NO;
}

- (void)dismiss {
    if (false) {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Cancel" message:@"Do you want to discard your change?" delegate:self cancelButtonTitle:@"NO" otherButtonTitles:@"YES", nil] autorelease];
        [alert show];
    } else {
        [self.navigationController popViewControllerAnimated:YES];
    }
}

- (void)submit {
    _doneButton.enabled = NO;
    _cancelButton.enabled = NO;
    
    if ([[SLDataController sharedInstance] sendRating:[NSNumber numberWithInt:2] offerCodeId:_offer.offerCodeId]) {
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
    } else if (buttonIndex == 1) {
        // dismiss
        [self.navigationController popViewControllerAnimated:YES];
    }
}

@end
