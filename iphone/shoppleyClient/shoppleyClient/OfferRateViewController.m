//
//  OfferRateViewController.m
//  shoppleyClient
//
//  Created by yod on 6/20/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferRateViewController.h"

#import "SLDataController.h"
#import "SLTableItem.h"
#import "SLTableViewDataSource.h"

@implementation OfferRateViewController
@synthesize new_value = _new_value;

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [self init])) {
        _offer = [[query objectForKey:@"offer"] retain];
        self.new_value = _offer.rating;
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
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    TT_RELEASE_SAFELY(_cancelButton);
    TT_RELEASE_SAFELY(_doneButton);
    TT_RELEASE_SAFELY(_new_value);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.tableView.scrollEnabled = NO;
    self.tableView.allowsSelection = YES;
    
    NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
    for (int i = 0; i <= 5; i++) {
        [items addObject:[SLStarsTableItem itemWithNumberofStars:[NSNumber numberWithInt:i]]];
    }
    self.dataSource = [SLListDataSource dataSourceWithItems:items];
    [self.tableView selectRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0] animated:YES scrollPosition:UITableViewScrollPositionNone];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    [self.tableView selectRowAtIndexPath:[NSIndexPath indexPathForRow:[_offer.rating intValue] inSection:0] animated:YES scrollPosition:UITableViewScrollPositionNone];
}

- (void)dismiss {
    if ([_new_value isEqualToNumber:_offer.rating]) {
        [self.navigationController popViewControllerAnimated:YES];
    } else {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"" message:@"Do you want to discard your change?" delegate:self cancelButtonTitle:@"NO" otherButtonTitles:@"YES", nil] autorelease];
        [alert show];
    }
}

- (void)submit {
    _doneButton.enabled = NO;
    _cancelButton.enabled = NO;
    
    if ([[SLDataController sharedInstance] sendRating:self.new_value offerCodeId:_offer.offerCodeId]) {
        _offer.rating = self.new_value;
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

- (void)didSelectObject:(id)object atIndexPath:(NSIndexPath *)indexPath {
    [super didSelectObject:object atIndexPath:indexPath];
    
    SLStarsTableItem* item = object;
    self.new_value = item.numberOfStars;
}

@end
