//
//  PastOffersViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/26/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "PastOffersViewController.h"

#import "SLPastOffer.h"
#import "SLTableViewDataSource.h"

@implementation PastOffersViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Past Offers";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_past_offers.png"] tag:0] autorelease];
        
        self.tableViewStyle = UITableViewStylePlain;
        self.variableHeightRows = YES;
    }
    return self;
}

- (void)createModel {
    _offers = [[[SLDataController sharedInstance] obtainPastOffersWithDelegate:self forcedDownload:NO] retain];
    
    if (_offers) {
        TTDPRINT(@"%@", _offers);
        NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i < [_offers count]; i++) {
            SLPastOffer* offer = [_offers objectAtIndex:i];
            [items addObject:[SLPastOfferTableItem itemWithOffer:offer URL:nil]];
        }
        self.dataSource = [SLListDataSource dataSourceWithItems:items];
    } else {
        self.dataSource = [TTListDataSource dataSourceWithObjects:
                           [TTTableActivityItem itemWithText:@"Processing..."],
                           nil];
    }
}

@end
