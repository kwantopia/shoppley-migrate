//
//  SLSelectAmountViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLSelectAmountViewController.h"


@implementation SLSelectAmountViewController
@synthesize delegate = _delegate, amountField = _amountField, unitSelector = _unitSelector;

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    self = [super init];
    if (self) {
        self.title = @"Select Date";
        self.tableViewStyle = UITableViewStyleGrouped;
        self.variableHeightRows = YES;
        self.tableView.scrollEnabled = NO;
        
        self.delegate = [query objectForKey:@"delegate"];
        NSNumber* amount = [query objectForKey:@"amount"];
        NSNumber* unit = [query objectForKey:@"unit"];
        
        self.amountField = [[[UITextField alloc] init] autorelease];
        self.amountField.font = [UIFont boldSystemFontOfSize:16];
        self.amountField.keyboardType = UIKeyboardTypeDecimalPad;
        self.amountField.clearButtonMode = UITextFieldViewModeWhileEditing;
        self.amountField.placeholder = @"Amount";
        if (amount) {
            self.amountField.text = [NSString stringWithFormat:@"%@", amount];
        }
        
        self.unitSelector = [[[UISegmentedControl alloc] initWithItems:[NSArray arrayWithObjects:@"$", @"%", nil]] autorelease];
        self.unitSelector.segmentedControlStyle = UISegmentedControlStylePlain;
        self.unitSelector.frame = CGRectMake(10, 10, 300, self.unitSelector.frame.size.height);
        self.unitSelector.center = CGPointMake(160,30);
        [self.unitSelector addTarget:self action:@selector(selectUnit) forControlEvents:UIControlEventValueChanged];
        if (unit) {
            self.unitSelector.selectedSegmentIndex = [unit intValue] - 1;
        } else {
            self.unitSelector.selectedSegmentIndex = 0;
        }
    }
    return self;
}

- (void)createModel {
    self.dataSource = [TTListDataSource dataSourceWithObjects:self.amountField, nil];
    
    UIView* headerView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, self.unitSelector.frame.size.height + 20)] autorelease];
    [headerView addSubview:self.unitSelector];
    self.tableView.tableHeaderView = headerView;
    
    [self.amountField becomeFirstResponder];
}

- (void)selectUnit {
    [self.delegate didselectUnit:[NSNumber numberWithInt:(self.unitSelector.selectedSegmentIndex + 1)]];
}

-(void) viewWillDisappear:(BOOL)animated {
    NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
    [f setNumberStyle:NSNumberFormatterDecimalStyle];
    NSNumber* amount = [f numberFromString:self.amountField.text];
    
    if (amount != nil) {
        [self.delegate didSelectAmount:amount];
    }
    [super viewWillDisappear:animated];
}

@end
