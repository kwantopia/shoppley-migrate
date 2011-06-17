//
//  SLTableViewDataSource.m
//  shoppleyClient
//
//  Created by yod on 6/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableViewDataSource.h"

#import "SLCurrentOffer.h"
#import "SLTableItemCell.h"

@implementation SLListDataSource

- (Class)tableView:(UITableView*)tableView cellClassForObject:(id) object { 
    if ([object isKindOfClass:[SLCurrentOfferTableItem class]]) {
        return [SLCurrentOfferTableItemCell class];
	} else {
		return [super tableView:tableView cellClassForObject:object];
	}
}

@end
