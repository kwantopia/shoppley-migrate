//
//  SLTableViewDataSource.m
//  shoppleyMerchant
//
//  Created by yod on 6/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableViewDataSource.h"

#import "SLActiveOffer.h"
#import "SLPastOffer.h"
#import "SLTableItem.h"
#import "SLTableItemCell.h"

@implementation SLListDataSource

- (Class)tableView:(UITableView*)tableView cellClassForObject:(id) object { 
    if ([object isKindOfClass:[SLActiveOfferTableItem class]]) {
        return [SLActiveOfferTableItemCell class];
	} else if ([object isKindOfClass:[SLPastOfferTableItem class]]) {
        return [SLPastOfferTableItemCell class];
	} else if ([object isKindOfClass:[SLRightValueTableItem class]]) {
        return [SLRightValueTableItemCell class];
	} else if ([object isKindOfClass:[SLStarsTableItem class]]) {
        return [SLStarsTableItemCell class];
	} else if ([object isKindOfClass:[SLRightStarsTableItem class]]) {
        return [SLRightStarsTableItemCell class];
	} else {
		return [super tableView:tableView cellClassForObject:object];
	}
}

@end

@implementation SLSectionedDataSource

- (Class)tableView:(UITableView*)tableView cellClassForObject:(id) object { 
    if ([object isKindOfClass:[SLActiveOfferTableItem class]]) {
        return [SLActiveOfferTableItemCell class];
	} else if ([object isKindOfClass:[SLPastOfferTableItem class]]) {
        return [SLPastOfferTableItemCell class];
	} else if ([object isKindOfClass:[SLRightValueTableItem class]]) {
        return [SLRightValueTableItemCell class];
	} else if ([object isKindOfClass:[SLStarsTableItem class]]) {
        return [SLStarsTableItemCell class];
	} else if ([object isKindOfClass:[SLRightStarsTableItem class]]) {
        return [SLRightStarsTableItemCell class];
	} else {
		return [super tableView:tableView cellClassForObject:object];
	}
}

@end